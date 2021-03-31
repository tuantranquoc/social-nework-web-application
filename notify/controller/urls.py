from django.urls import path
from notify.controller import rest as signal_room_api

urlpatterns = [
    path('room', signal_room_api.get_signal_room),
]