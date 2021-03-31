# mysite/asgi.py
import os
from django.urls import re_path

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import chatv0.routing
# from chatv0 import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "redditv1.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": AuthMiddlewareStack(
        URLRouter(
            chatv0.routing.websocket_urlpatterns
        )
    ),
})

# application = ProtocolTypeRouter({

#     "websocket": AuthMiddlewareStack(
#         URLRouter([
#             re_path(r"^front(end)/$", consumers.ChatConsumer.as_asgi()),
#             chatv0.routing.websocket_urlpatterns
#         ])
#     ),

# })