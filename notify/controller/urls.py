from django.urls import path
from notify.controller import rest as signal_room_api

urlpatterns = [
    path('signal/room', signal_room_api.get_signal_room),
    path('list', signal_room_api.get_notification_list),
    path('change', signal_room_api.change_notify_status),
    path('status/false/count', signal_room_api.count_notification_has_not_view),

]