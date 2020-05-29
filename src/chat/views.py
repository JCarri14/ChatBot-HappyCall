from django.shortcuts import render
from chat.models import *

def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):    
    context = {
        'room_name': room_name
    }
    return render(request, 'chat/room-view.html', context)

