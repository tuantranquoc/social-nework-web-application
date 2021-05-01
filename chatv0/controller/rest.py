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
from service.chat import chat_service
User = get_user_model()

@api_view(["POST"])
def create_chat_room(request):
    """
    ``POST`` Create chatroom between user

    **Example request**:
    .. code-block:: json

        {
            "target_user":"target_user_name"
        }
    """
    return chat_service.create_chat_room(request)

@api_view(["GET","POST"])
def find_room(request):
    return chat_service.find_room(request)

@api_view(["GET"])
def get_all_room(request):
    """
    ``GET`` all chat room of current ``USER``
    """
    return chat_service.get_rooms_by_user(request)

# @api_view(["GET","POST"])
# def get_room_by_user(request):
#     return chat_service.get_rooms_by_user(request)

@api_view(["POST"])
def get_user_info_by_room_id(request):
    """
    ``GET`` get target profile info from room id

    **Example request**:
    .. code-block:: json

        {
            "id":"room_id"
        }
    """
    return chat_service.get_user_info_by_room_id(request)


@api_view(["POST"])
def get_lasted_message(request):
    """
    ``GET`` get lasted message

    **Example request**:
    .. code-block:: json

        {
            "id":"room_id"
        }
    """
    return chat_service.get_lasted_message(request)


@api_view(["POST"])
def get_message_f(request):
    """
    ``GET`` get lasted message

    **Example request**:
    .. code-block:: json

        {
            "id":"room_id",
            "page_size":"page_size"
        }
    """
    return chat_service.get_message_f(request)