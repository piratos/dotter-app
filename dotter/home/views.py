import json
import logging
import os

from subprocess import check_call, CalledProcessError
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from home.models import Graph
from home.forms import UserForm
from uuid import uuid4

from random import randint
from time import sleep

logger = logging.getLogger('home.views')
tracing = settings.OPENTRACING_TRACING

def index(request):
    return render(request, 'index.html', locals())

def register(request):
    registered = False
    if request.method == 'GET':
        # display registration form
        user_form = UserForm()
    elif request.method == 'POST':
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            registered = True
            logger.info('User %s registered', user.username)
        else:
            logger.error(user_form.errors)
    return render(request, 'register.html', locals())

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home:index'))
            return HttpResponse("This account is not active")
        logger.info("login failed %s %s", username, password)
        return HttpResponse("Invalid login details given")
    return render(request, 'login.html', {})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home:index'))

def graphing(request):
    graphs = list_graphs(request)
    if request.method == 'POST':
        name = request.POST['name']
        content = request.POST['content']
        user = request.user
        new_graph = create_graph(
            request, name, content, user, parent_view='graphing'
        )
        wait_random(request)
        graph_name = new_graph.name
        graph_public_link = new_graph.public_link
        if not new_graph:
            return HttpResponseRedirect(reverse('home:graphing'))
    return render(request, 'graph.html', locals())

@tracing.trace(view=False)
def create_graph(request, name, content, user, parent_view=None):
    random_folder_name = str(uuid4())
    # create a folder for the files
    folder_path = os.path.join(settings.DATA_PATH, random_folder_name)
    os.mkdir(folder_path)
    dotfile_name = os.path.join(folder_path, name + '.dot')
    pngfile_name = os.path.join(folder_path, name + '.png')
    public_link = os.path.join(random_folder_name, name + '.png')
    with open(dotfile_name, 'w') as dotfile:
        dotfile.write(content)
    try:
        check_call(['dot', '-Tpng', dotfile_name, '-o', pngfile_name])
    except CalledProcessError:
        return None
    # create graph object now
    graph = Graph(
        content=content,
        name=name,
        author=user,
        dot=dotfile_name,
        png=pngfile_name,
        public_link=public_link,
    )
    graph.save()
    return graph

@tracing.trace(view=False)
def wait_random(request):
    sleep(randint(1, 5))

@tracing.trace(view=False)
def list_graphs(request):
    return Graph.objects.filter(author=request.user)