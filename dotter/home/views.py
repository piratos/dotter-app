from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from home.forms import UserForm

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
