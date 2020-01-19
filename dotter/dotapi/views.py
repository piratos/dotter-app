from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from django.core import serializers
from subprocess import check_call
from uuid import uuid4
from dotapi.models import Graph
import os

@login_required
def generate_graph(request):
    if request.method != 'POST':
        return HttpResponse("{'fail': 'Need POST request'}")
    content = request.POST.get('content')
    name = request.POST.get('name')
    user = request.user
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
    except CalledProcessorError:
        return HttpResponse("{'fail': 'Dot command failed'}")
    # create graph object now
    graph = Graph(
        content = content,
        name = name,
        author = user,
        dot = dotfile_name,
        png = pngfile_name,
        public_link = public_link,
    )
    graph.save()
    return serializers.serialize('json', [graph, ])
