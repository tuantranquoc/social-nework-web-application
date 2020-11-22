import base64

from django.core.files.base import ContentFile
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from account.models import Profile
from community.models import Community
from post.models import PositivePoint
from post.serializers import CommunityGraphSerializer, CommunitySerializer
from redditv1.message import Message
from django.utils import timezone
from function.file import get_image
import datetime
from service.community import community_service

User = get_user_model()


@api_view(["POST"])
def create_community(request):
    return community_service.create_community(request)


@api_view(["POST", "GET"])
def get_community(request):
    return community_service.get_community(request)


@api_view(["GET"])
def get_list_community_by_user(request):
    return community_service.get_list_community_by_user(request)


@api_view(["POST"])
def community_action(request):
    return community_service.community_action(request)


@api_view(["GET"])
def get_list_community(request):
    return community_service.get_list_community(request)


@api_view(['GET'])
def change_state(request, community_type):
    return community_service.change_state(request, community_type)


@api_view(['POST'])
def community_update_via_react_view(request):
    return community_service.community_update(request)


@api_view(['GET', 'POST'])
def recommend_sub_community(request, community):
    return community_service.recommend_sub_community(request, community)


@api_view(['GET', 'POST'])
def recommend_community(request):
    return community_service.recommend_community(request)


@api_view(['GET', 'POST'])
def community_graph(request):
    return community_service.community_graph(request)


@api_view(['GET', 'POST'])
def community_mod_action(request):
    return community_service.mod_action(request)

@api_view(['GET', 'POST'])
def get_member_list(request):
    return community_service.member_list(request)

def timestamp_in_the_past_by_day(days):
    return timezone.now() - datetime.timedelta(days)
