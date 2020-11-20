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
from redditv1.name import ModelName
from function.paginator import get_paginated_queryset_response
from function.file import isValidHexaCode
import datetime
from service.post.post_service import timestamp_in_the_past_by_day


def create_community(request):
    if request.user.is_authenticated:
        community = request.data.get("community")
        sub_community = request.data.get("sub_community")
        background = request.data.get("background")
        description = request.data.get("description")
        avatar = request.data.get("avatar")
        rule = request.data.get("rule")
        background_color = request.data.get("background_color")
        if request.user.positivepoint.point <= 10:
            return Response({Message.SC_NOT_ENOUGH_POINT}, status=400)
        if not sub_community:
            if Community.objects.filter(community_type=community):
                return Response({Message.SC_CM_EXIST}, status=200)
            if not request.user.is_staff:
                return Response({Message.SC_PERMISSION_DENIED}, status=403)
            community = Community.objects.create(community_type=community,
                                                 description=description,
                                                 rule=rule, creator=request.user)
            if isValidHexaCode(background_color):
                community.background_color = background_color
            if background:
                if len(background) > len('data:,'):
                    community.background = get_image(background)
            if avatar:
                if len(avatar) > len('data:,'):
                    community.avatar = get_image(background)
            community.save()
            positive_point = PositivePoint.objects.filter(
                user=request.user).first()
            positive_point.point = positive_point.point - 10
            positive_point.save()
            serializer = CommunitySerializer(community)
            return Response(serializer.data, status=201)
        if not Community.objects.filter(community_type=community):
            return Response({Message.SC_CM_NOT_FOUND}, status=204)

        community_exist = Community.objects.filter(
            community_type=sub_community).first()
        if community_exist:
            return Response({Message.SC_CM_EXIST}, status=200)
        parent = Community.objects.filter(community_type=community).first()
        community = Community.objects.create(community_type=sub_community,
                                             parent=parent,
                                             description=description,
                                             rule=rule, creator=request.user)
        if isValidHexaCode(background_color):
            community.background_color = background_color
        positive_point = PositivePoint.objects.filter(
            user=request.user).first()
        positive_point.point = positive_point.point - 10
        positive_point.save()
        if background:
            if len(background) > len('data:,'):
                community.background = get_image(background)
        if avatar:
            if len(avatar) > len('data:,'):
                community.avatar = get_image(background)
        community.save()
        serializer = CommunitySerializer(community)
        return Response(serializer.data, status=201)


def get_community(request):
    page_size = request.data.get("page_size")
    community_type = request.data.get('community')
    print(community_type)
    if community_type:
        community = Community.objects.filter(
            community_type__icontains=community_type)
        return get_paginated_queryset_response(community, request, page_size,
                                               ModelName.COMMUNITY)
    return Response({Message.SC_NOT_FOUND}, status=204)


def get_list_community_by_user(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        query = Community.objects.filter(user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.COMMUNITY)
    return Response({Message.SC_LOGIN_REDIRECT}, status=200)


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
        return Response({Message.SC_NOT_FOUND}, status=204)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


def get_list_community(request):
    page_size = request.data.get("page_size")
    query = Community.objects.all()
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.COMMUNITY)


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


def community_update(request):
    if not request.user.is_authenticated:
        return Response({}, status=401)
    user = request.user
    community_type = request.data.get('community_type')
    community = Community.objects.filter(
        creator=request.user, community_type=community_type).first()
    background = request.data.get("background")
    description = request.data.get("description")
    avatar = request.data.get("avatar")
    background_color = request.data.get("background_color")
    if background:
        community.background = get_image(background)
    if avatar:
        community.avatar = get_image(avatar)
    if description:
        community.description = description
    if background_color:
        if isValidHexaCode(background_color):
            community.background_color = background_color
    user.save()
    community.save()
    if not community.background or not community.avatar:
        return Response({Message.SC_BAD_IMG}, status=400)
    return Response({}, status=200)


def recommend_sub_community(request, community):
    page_size = request.data.get("page_size")
    sub_community = Community.objects.filter(parent__community_type=community)
    if request.user.is_authenticated:
        sub_community = Community.objects.filter(
            parent__community_type=community).exclude(user=request.user)
    return get_paginated_queryset_response(sub_community, request, page_size,
                                           ModelName.COMMUNITY)


def recommend_community(request):
    page_size = request.data.get("page_size")
    community = Community.objects.all().annotate(
        user_count=Count('user')).order_by('user_count')
    if request.user.is_authenticated:
        community = Community.objects.all().exclude(
            user=request.user).annotate(
                user_count=Count('user')).order_by('user_count')
    return get_paginated_queryset_response(community, request, page_size,
                                           ModelName.COMMUNITY)


def community_graph(request):
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    page_size = request.data.get('page_size')
    print('detect')
    if from_timestamp:
        print("timestamp: ", from_timestamp)
    if from_timestamp is not None and to_timestamp is not None:
        query = Community.objects.filter(
            timestamp__gte=from_timestamp,
            timestamp__lte=to_timestamp,
        )
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.COMMUNITY_GRAPH)
    query = Community.objects.filter(
        timestamp__gte=timestamp_in_the_past_by_day(30),
        timestamp__lte=timezone.now(),
    )
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.COMMUNITY_GRAPH)


