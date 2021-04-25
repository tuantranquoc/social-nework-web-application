from django.urls import path
from chatv0.controller import rest as chat_api

urlpatterns = [
    path('', chat_api.create_chat_room),
    path('find/', chat_api.find_room),
    path('all/', chat_api.get_all_room),
    # path('get/room', chat_api.get_room_by_user),
    path('room/detail', chat_api.get_user_info_by_room_id),
]