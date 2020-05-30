from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name="index"),
    path('control/', views.dashboard, name='dashboard'),
    path('control/<str:room_name>/', views.room_control, name='room-control'),
    path('<str:room_name>/', views.room, name='room'),
]