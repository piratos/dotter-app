from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from home.forms import UserForm
from dotapi.views import generate_graph
from dotapi.models import Graph

import json
import logging
logger = logging.getLogger('home.views')

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
            else:
                return HttpResponse("This account is not active")
        else:
            logger.info("login failed %s %s", username, password)
            return HttpResponse("Invalid login details given")
    else:
        return render(request, 'login.html', {})

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home:index'))

def graphing(request):
    graphs = Graph.objects.filter(author=request.user)
    if request.method == 'POST':
        graph_ser = generate_graph(request)
        graph_dict = json.loads(graph_ser)[0].get('fields')
        graph_name = graph_dict['name']
        graph_public_link = graph_dict['public_link']
        if graph_dict.get('fail'):
            return HttpResponseRedirect(reverse('home:graphing'))
    return render(request, 'graph.html',locals())
