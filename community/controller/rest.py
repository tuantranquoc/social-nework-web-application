import base64

from django.core.files.base import ContentFile
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from account.models import Profile
from community.models import Community, Member
from post.models import PositivePoint
from post.serializers import CommunityGraphSerializer, CommunitySerializer
from redditv1.message import Message
from django.utils import timezone
from function.file import get_image
import datetime
from service.community import community_service
from function.paginator import get_paginated_queryset_response
from redditv1.name import ModelName

User = get_user_model()


@api_view(["POST"])
def create_community(request):
    """
    ``POST`` ``CREATE_COMMUNITY``
    
    New ``Community`` require parent community to create

    **Example request**:
    .. code-block:: json

        {
            "community": "parent_community_name",
            "sub_community": "sub_community_name",
            "description":"RSA",
            "avatar":"optional",
            "rule":"optional",
            background_color:"optional-base64"
        }
    """
    return community_service.create_community(request)


@api_view(["POST"])
def get_community(request):
    """
    ``POST`` Return community info by ``community_name``

    New ``Community`` require parent community to create

    **Example request**:
    .. code-block:: json

        {
            "community": "community_name",
        }
    """
    return community_service.get_community(request)


@api_view(["GET", "POST"])
def get_list_community_by_user(request):
    """
    ``GET``, ``POST`` Return list of community followed by current user.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5",
        }
    """
    return community_service.get_list_community_by_user(request)


@api_view(["POST"])
def community_action(request):
    """
    ``POST`` ``Follow or UnFollow community``

    ``Action`` can be ``follow`` or ``un_follow``

    **Example request**:
    .. code-block:: json

        {
            "community": "community_name",
            "action":"follow"
        }
    """
    return community_service.community_action(request)


@api_view(["GET"])
def get_list_community(request):
    """
    ``GET`` Return list community
    """
    return community_service.get_list_community(request)


@api_view(['GET'])
def change_state(request, community_type):
    return community_service.change_state(request, community_type)


@api_view(['POST'])
def community_update_via_react_view(request):
    """
    ``POST`` ``UPDATE_COMMUNITY``

    **Example request**:
    .. code-block:: json

        {
            "community_type": "community name",
            "background": "sub_community_name",
            "description":"optional-base64",
            "avatar":"optional-base64",
            "rule":"optional",
            "background_color":"optional",
           "title_background_color":"optional",
           "description_background_color":"optional",
           "button_background_color":"optional",
           "button_text_color":"optional",
           "text_color":"optional",
           "post_background_color":"optional"
        }
    """
    return community_service.community_update(request)


@api_view(['GET', 'POST'])
def recommend_sub_community(request, community):
    """
    ``GET`` ``RECOMMEND SUB_COMMUNITY``

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    return community_service.recommend_sub_community(request, community)


@api_view(['GET', 'POST'])
def recommend_community(request):
    """
    ``GET`` ``RECOMMEND SUB_COMMUNITY``

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    return community_service.recommend_community(request)


@api_view(['GET', 'POST'])
def community_graph(request):
    return community_service.community_graph(request)


@api_view(['POST'])
def community_mod_action(request):
    """
    ``POST`` promote or demote user from provide community
    ``action`` can be ``promote`` or ``demote``
    **Example request**:
    .. code-block:: json
        {
            "community": "anime",
            "user_id":"user_id",
            "action":"promote"
        }
    """
    return community_service.mod_action(request)


@api_view(['GET', 'POST'])
def get_member_list(request):
    return community_service.member_list(request)


@api_view(['GET', 'POST'])
def blacklist(request):
    return community_service.add_use_to_community_blacklist(request)

@api_view(['POST'])
def hidden_post(request):
    """
    ``POST`` hidden post in community
    ``PERMISSION`` require are ``author, mod and admin``
    ``action`` can be ``promote`` or ``demote``
    **Example request**:
    .. code-block:: json
        {
            "post_id":"post_id"
        }
    """
    return community_service.hidden_post(request)



# @api_view(['GET'])
# def get_followed_community_by_username(request, username):
#     return community_service.get_followed_community_by_username(
#         request, username)


@api_view(['GET'])
def get_followed_community_by_username(request, username):
    user = User.objects.filter(username=username).first()
    print("un", username)
    if user:
        member = Member.objects.filter(user=user).first()
        if member:
            member_info = member.member_info.all()
            community_list = Community.objects.filter(community_type__in=[x.community.community_type for x in member_info])
            return get_paginated_queryset_response(community_list, request,10,ModelName.COMMUNITY)
    return Response({Message.SC_NOT_FOUND}, status=200)

def timestamp_in_the_past_by_day(days):
    return timezone.now() - datetime.timedelta(days)


