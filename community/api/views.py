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
import datetime

User = get_user_model()


def get_paginated_queryset_response(query_set, request, page_size):
    paginator = PageNumberPagination()
    if not page_size:
        page_size = 20
    paginator.page_size = page_size
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = CommunitySerializer(paginated_qs,
                                     many=True,
                                     context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
def create_community(request):
    if request.user.is_authenticated:
        community = request.data.get("community")
        sub_community = request.data.get("sub_community")
        background = request.data.get("background")
        description = request.data.get("description")
        avatar = request.data.get("avatar")
        rule = request.data.get("rule")
        if not Community.objects.filter(community_type=community):
            return Response({Message.SC_NOT_FOUND}, status=400)
        if request.user.positivepoint.point <= 10:
            return Response({Message.SC_NOT_ENOUGH_POINT}, status=400)
        parent = Community.objects.filter(community_type=community).first()
        community = Community.objects.create(community_type=sub_community,
                                             parent=parent,
                                             description=description,
                                             rule=rule)
        positive_point = PositivePoint.objects.filter(
            user=request.user).first()
        positive_point.point = positive_point.point - 10
        positive_point.save()
        if background:
            format, imgstr = background.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            community.background = image
        if avatar:
            format, imgstr = avatar.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            community.avatar = image
        community.save()
        serializer = CommunitySerializer(community)
        return Response(serializer.data, status=201)


@api_view(["POST","GET"])
def get_community(request):
    page_size = request.data.get("page_size")
    community_type = request.data.get('community')
    if community_type:
        community = Community.objects.filter(community_type=community_type)
        return get_paginated_queryset_response(community, request, page_size)
    return Response({Message.SC_BAD_RQ}, status=400)


@api_view(["GET"])
def get_list_community_by_user(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        query = Community.objects.filter(user=request.user)
        return get_paginated_queryset_response(query, request, page_size)
    return Response({Message.SC_LOGIN_REDIRECT}, status=200)


@api_view(["POST"])
def community_action(request):
    if request.user.is_authenticated:
        community_type = request.data.get('community')
        action = request.data.get('action')
        community = Community.objects.filter(
            community_type=community_type).first()
        if community:
            if action == "follow":
                community.user.add(request.user)
            if action == "un_follow":
                community.user.remove(request.user)
            return Response({Message.SC_OK}, status=200)
        return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


@api_view(["GET"])
def get_list_community(request):
    page_size = request.data.get("page_size")
    query = Community.objects.all()
    return get_paginated_queryset_response(query, request, page_size)


@api_view(['GET'])
def change_state(request, community_type):
    if request.user.is_authenticated:
        if community_type:
            community = Community.objects.filter(
                creator=request.user, community_type=community_type).first()
            if community:
                community.state = not community.state
                community.save()
                return Response(Message.SC_OK, status=200)
            return Response(Message.SC_PERMISSION_DENIED, status=403)
        return Response(Message.SC_BAD_RQ, status=400)
    return Response(Message.SC_LOGIN_REDIRECT, status=403)


@api_view(['POST'])
def community_update_via_react_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return Response({}, status=401)
    user = request.user
    community_type = request.data.get('community_type')
    community = Community.objects.filter(
        creator=request.user, community_type=community_type).first()
    background = request.data.get("background")
    description = request.data.get("description")
    avatar = request.data.get("avatar")
    if background:
        data = request.data.get("background")
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        community.background = image
    if avatar:
        data = request.data.get("avatar")
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        community.avatar = image
    if description:
        community.description = description
    user.save()
    community.save()
    if not community.background or not community.avatar:
        return Response({Message.SC_BAD_IMG}, status=400)
    return Response({}, status=200)


@api_view(['GET', 'POST'])
def recommend_sub_community(request, community):
    page_size = request.data.get("page_size")
    sub_community = Community.objects.filter(
        parent__community_type=community).exclude(user=request.user)
    return get_paginated_queryset_response(sub_community, request, page_size)


@api_view(['GET', 'POST'])
def recommend_community(request):
    page_size = request.data.get("page_size")
    community = Community.objects.all().exclude(user=request.user).annotate(
        user_count=Count('user')).order_by('user_count')
    return get_paginated_queryset_response(community, request, page_size)


@api_view(['GET', 'POST'])
def community_graph(request):
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    page_size = request.data.get('page_size')
    if from_timestamp:
        print("timestamp: ", from_timestamp)
    if from_timestamp is not None and to_timestamp is not None:
        query = Community.objects.filter(
            timestamp__gte=from_timestamp,
            timestamp__lte=to_timestamp,
        )
        return get_paginated_queryset_response_graph(query, request, page_size)
    query = Community.objects.filter(
        timestamp__gte=timestamp_in_the_past_by_day(30),
        timestamp__lte=timezone.now(),
    )
    return get_paginated_queryset_response_graph(query, request, page_size)


def timestamp_in_the_past_by_day(days):
    return timezone.now() - datetime.timedelta(days)


def get_paginated_queryset_response_graph(query_set, request, page_size):
    paginator = PageNumberPagination()
    if page_size:
        paginator.page_size = page_size
    else:
        paginator.page_size = 50
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = CommunityGraphSerializer(paginated_qs,
                                          many=True,
                                          context={"request": request})
    return paginator.get_paginated_response(serializer.data)