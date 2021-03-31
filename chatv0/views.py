from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
import json


# Create your views here.


def index(request):
    return render(request, 'chat/index.html')


@login_required
def room(request, room_name):
    return render(request, 'chat/chat.html', {
        'room_name': room_name,
        'username': request.user.username
    })


# need api for list of room with the user in it maybe ten is good enough
