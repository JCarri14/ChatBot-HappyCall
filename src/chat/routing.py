# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/control/$', consumers.DashboardConsumer),
    re_path(r'ws/chat/control/(?P<room_name>\w+)/$', consumers.ReadOnlyChatConsumer),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
]