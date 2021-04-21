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


@api_view(["GET","POST"])
def profile_list_view(request):
    """
    ``GET`` view all profile info.

    **Example post request**:
    .. code-block:: json

        {
            "page_size":"5"
        }
    """
    return profile_service.profile_list_view(request)


@api_view(["GET"])
def profile_detail_view(request, username):
    """
    ``GET`` view profile detail info by provied username.
    """
    return profile_service.profile_detail_view(request, username)


@api_view(["GET", "POST"])
def profile_current_detail_view(request):
    """
    ``GET`` view profile detail info of current user.
    """
    return profile_service.profile_current_detail_view(request)


@api_view(['GET', 'POST'])
def profile_detail_api_view(request, username):
    return profile_service.profile_current_detail_view(request, username)


@api_view(['POST'])
def profile_image_post(request):
    """
    ``POST`` update profile image.

    **Example post request**:
    .. code-block:: json

        {
            "img":"base64"
        }
    """
    return profile_service.profile_image_post(request)


@api_view(['GET', 'POST'])
def profile_avatar_post(request):
    return profile_service.profile_avatar_post(request)


@api_view(['GET', 'POST'])
def profile_background_post(request, *args, **kwargs):
    """
    ``POST`` update profile avatar.

    **Example post request**:
    .. code-block:: json

        {
            "img":"base64"
        }
    """
    return profile_service.profile_background_post(request)


@api_view(['POST'])
def profile_update_via_react_view(request, *args, **kwargs):
    """
    ``POST`` ``UPDATE_PROFILE``

    **Example request**:
    .. code-block:: json

        {
            "first_name": "community name",
            "last_name": "sub_community_name",
            "location":"optional-base64",
            "bio":"optional-base64",
            "email":"optional",
            "avatar":"base64-optional",
            "background":"base64-optional"
            "background_color":"optional",
           "title_background_color":"optional",
           "description_background_color":"optional",
           "button_background_color":"optional",
           "button_text_color":"optional",
           "text_color":"optional",
           "post_background_color":"optional"
        }
    """
    return profile_service.profile_update_via_react_view(request)


@api_view(['GET','POST'])
def get_following_profiles(request, username):
    """
    ``GET`` Return list of following profile

    **Example request**:
    .. code-block:: json

        {
            "page_size":"5"
        }
    """
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
    """
    ``POST`` ``Follow or UnFollow differant USER``

    ``Action`` can be ``follow`` or ``un_follow``

    **Example request**:
    .. code-block:: json

        {
            "community": "community_name",
            "action":"follow"
        }
    """
    return profile_service.profile_action(request)


@api_view(['POST', 'GET'])
def search(request):
    """
    ``GET``, ``POST`` Return list of profiles by keywords provide.
    
    ``search_type`` can be optional

    **Example request**:
    .. code-block:: json

        {
            "page_size":"5",
            "key_word":"key_word"
            "search_type":"community"
        }
    """
    return profile_service.search(request)


@api_view(['POST', 'GET'])
def search_v0(request):
    """
    ``GET``, ``POST`` Return list of profiles by keywords provide.
    
    ``search_type`` can be ``user`` or ``community``

    **Example request**:
    .. code-block:: json

        {
            "page_size":"5",
            "key_word":"key_word"
            "search_type":"community"
        }
    """
    return profile_service.search_v0(request)


@api_view(['GET'])
def recommend_user_from_profile(request, username):
    """
    ``GET`` list of follower from current user
    """
    return profile_service.recommend_user_from_profile(request, username)


@api_view(['GET'])
def recommend_user_from_feed(request, *args, **kwargs):
    """
    ``GET`` list of follower from current user
    """
    return profile_service.recommend_user_from_feed(request)


@api_view(['GET'])
def recommend_user_from_global(request):
    """
    ``GET`` list of follower from current user
    """
    return profile_service.recommend_user_from_global(request)
