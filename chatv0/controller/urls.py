from django.urls import path
from chatv0.controller import rest as chat_api

urlpatterns = [
    path('room/user/<str:target_user>', chat_api.create_chat_room),
    path('find/', chat_api.find_room),
    path('all/', chat_api.get_all_room),
    # path('get/room', chat_api.get_room_by_user),
    path('room/detail', chat_api.get_user_info_by_room_id),
    path('room/lasted/message', chat_api.get_lasted_message),
    path('room/set/message', chat_api.set_message_read),
    path('room/yet/message', chat_api.count_total_message_not_read_in_all_room)
]