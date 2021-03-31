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
from service.profile import profile_service
User = get_user_model()


@api_view(["GET"])
def profile_list_view(request):
    return profile_service.profile_list_view(request)


@api_view(["GET"])
def profile_detail_view(request, username):
    return profile_service.profile_detail_view(request, username)


@api_view(["GET","POST"])
def profile_current_detail_view(request):
    return profile_service.profile_current_detail_view(request)


@api_view(['GET', 'POST'])
def profile_detail_api_view(request, username):
    return profile_service.profile_current_detail_view(request, username)


@api_view(['GET', 'POST'])
def profile_image_post(request):
    return profile_service.profile_image_post(request)


@api_view(['GET', 'POST'])
def profile_avatar_post(request):
    return profile_service.profile_avatar_post(request)


@api_view(['GET', 'POST'])
def profile_background_post(request, *args, **kwargs):
    return profile_service.profile_background_post(request)


@api_view(['POST'])
def profile_update_via_react_view(request, *args, **kwargs):
    return profile_service.profile_update_via_react_view(request)


@api_view(['GET'])
def get_following_profiles(request, username):
    return profile_service.get_following_profiles(request, username)


@api_view(['GET', 'POST'])
def login_via_react_view(request):
    return profile_service.login_via_react_view(request)


@api_view(['GET', 'POST'])
def register_via_react_view(request):
    return profile_service.register_via_react_view(request)


@api_view(['GET', 'POST'])
def logout_view_js(request):
    return profile_service.logout_view_js(request)


@api_view(['POST'])
def profile_action(request):
    return profile_service.profile_action(request)


@api_view(['POST', 'GET'])
def search(request):
    return profile_service.search(request)


@api_view(['POST', 'GET'])
def search_v0(request):
    return profile_service.search_v0(request)


@api_view(['GET'])
def recommend_user_from_profile(request, username):
    """
    get list follower from this acc
    profile -> follower acc -> max follower count okay >?
    """
    return profile_service.recommend_user_from_profile(request, username)


@api_view(['GET'])
def recommend_user_from_feed(request, *args, **kwargs):
    """
    get all follower list from feed -> feed mean that all the tweet that user has follow
    get all the follower profile from em
    """
    return profile_service.recommend_user_from_feed(request)


@api_view(['GET'])
def recommend_user_from_global(request):
    return profile_service.recommend_user_from_global(request)
