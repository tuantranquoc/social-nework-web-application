import base64
import operator
from functools import reduce

from django.contrib.auth import authenticate, login, get_user_model, logout
from django.core.files.base import ContentFile
from django.db.models import Q, Count
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from account.models import Profile
from account.serializers import PublicProfileSerializer
from post.models import Post
from post.serializers import PostSerializer
from redditv1.message import Message
from function.file import get_image
from function.paginator import get_paginated_queryset_response
from redditv1.name import ModelName
from community.models import Community
from service.notify import notify_service
from notify.models import UserNotify
User = get_user_model()

@api_view(["GET"])
def get_signal_room(request):
    """
    ``GET`` Return ``USER`` signal room
    """
    return notify_service.get_signal_room(request)

@api_view(["GET"])
def get_notification_list(request):
    """
    ``GET`` Return list of notify of current user
    """
    return notify_service.get_notify_list(request)

@api_view(["POST"])
def change_notify_status(request):
    """
    ``POST`` Change notify status

    **Example request**:
    .. code-block:: json

        {
            "id":"notification_id"
        }
    """
    return notify_service.change_notify_status(request)

@api_view(["GET"])
def count_notification_has_not_view(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    user = request.user
    notify_list = UserNotify.objects.filter(user=request.user)
    count = 0
    for n in notify_list:
        if n.status==False:
            count += 1
    return Response({"notification_not_read_count":count}, status=200)

