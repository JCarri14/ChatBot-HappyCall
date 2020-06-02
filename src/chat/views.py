from django.shortcuts import render
from chat.models import *
from chat.ddbb.MongoODMManager import MongoODMManager

def index(request):
    return render(request, 'chat/index.html', {})

def room(request, room_name):    
    context = {
        'room_name': room_name
    }
    return render(request, 'chat/room-view.html', context)

def dashboard(request):
    dbManager = MongoODMManager("localhost", "27017", "happy_call")
    c = list(dbManager.get_conversations())
    if c and len(c) > 0:
        c = [c[i].name for i in range(len(c)) if c[i].name]
    context = {
        'conversations': c
    }
    return render(request, 'chat/dashboard.html', context)

def room_control(request, room_name):
    dbManager = MongoODMManager("localhost", "27017", "happy_call")
    m = dbManager.get_conversation_messages("chat_" + room_name)
    context = {
        'room_name': room_name,
        'messages': m,
    }
    return render(request, 'chat/room-read-view.html', context)

