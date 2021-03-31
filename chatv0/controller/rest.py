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

@api_view(["GET","POST"])
def create_chat_room(request):
    return chat_service.create_chat_room(request)

@api_view(["GET","POST"])
def find_room(request):
    return chat_service.find_room(request)

@api_view(["GET","POST"])
def get_all_room(request):
    return chat_service.get_rooms_by_user(request)