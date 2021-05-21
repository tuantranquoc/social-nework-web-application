from django.urls import re_path

from . import consumers
from chatv0.consumer import chat_consumer, signal_consumer, key_exchange_consumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', chat_consumer.ChatConsumer.as_asgi()),
    re_path(r'ws/signal/(?P<room_name>\w+)/$', signal_consumer.SignalConsumer.as_asgi()),
    re_path(r'ws/key_exchange/(?P<room_name>\w+)/$', key_exchange_consumer.SignalConsumer.as_asgi()),
]