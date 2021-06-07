from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from post import rank
from post.models import Post, Comment, CommentPoint
from rest_framework.response import Response
from post.serializers import CommentSerializer, CommentGraphSerializer
from redditv1.message import Message
from function.paginator import get_paginated_queryset_response
from redditv1.name import ModelName, CommentState
from service.post.post_service import timestamp_in_the_past_by_day
from chatv0.models import Room
from django.contrib.auth import get_user_model
from django.db.models import Q
from function.paginator import get_paginated_queryset_response
from account.models import Profile
from chatv0.models import Message as ChatMessage
User = get_user_model()


def create_chat_room(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    target_user = request.data.get('target_user')
    if target_user:
        target = User.objects.filter(username=target_user).first()
        print(target.username)
        room = Room.objects.filter(user__username=target.username)
        room = room.filter(user__username=request.user)
        if room:
            return Response({Message.SC_OK}, status=200)
        room = Room.objects.create()
        room.user.add(target)
        room.user.add(request.user)
        room.save()
        return Response({Message.SC_OK}, status=201)
    return Response({Message.SC_OK}, status=400)


def find_room(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    target_user = request.data.get('target_user')
    # if not Room.objects.filter(user=request.user).first():
    if target_user:
        target = User.objects.filter(username=target_user).first()
        print(target.username)
        room = Room.objects.filter(user=target)
        if room:
            print(room.first())
            return Response({Message.SC_OK}, status=201)
        # room.user.add(target)
        # room.user.add(request.user)
        # room.save()
        # return Response({Message.SC_OK}, status=201)
    return Response({Message.SC_OK}, status=400)


def get_rooms_by_user(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    page_size = request.data.get("page_size")
    user = request.user
    rooms = Room.objects.filter(user=user)
    print("count room", rooms.count(), user)
    return get_paginated_queryset_response(rooms, request, page_size,
                                                   ModelName.CHAT)

# def get_room_by_user(request):
#     if not request.user.is_authenticated:
#         return Response({Message.SC_NO_AUTH}, status=401)


def get_user_info_by_room_id(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    room_id = request.data.get("id")
    user = request.user
    room = Room.objects.filter(pk=room_id).first()
    if room:
        target_user = room.user.all()
        profile = Profile.objects.filter(user__in=target_user)
        profile = profile.exclude(user=user)
        return get_paginated_queryset_response(profile, request, 2,
                                           ModelName.PROFILE)
    return Response({Message.SC_NOT_FOUND}, status=401)

def get_lasted_message(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    room_id = request.data.get("id")
    if room_id:
        user = request.user
        room = Room.objects.filter(pk=room_id).first()
        if room:
            message_list = ChatMessage.objects.filter(room__id=room_id).order_by("-created_at").first()
            dest_user = Room.objects.filter(pk=room_id).first().user.exclude(username=user.username).first()
            print("dest user", dest_user)
            message_list_not_read = ChatMessage.objects.filter(room__id=room_id, state=False, author=dest_user)
            room_list = Room.objects.filter(user=request.user)
            message_list_not_read_all_room_count = 0
            for r in room_list:
                message_list_not_read_all_room = ChatMessage.objects.filter(room__id=r.id, state=False)
                if message_list_not_read_all_room.count() != 0:
                    message_list_not_read_all_room_count += 1
            count = 0
            for m in message_list_not_read:
                if m.state == False:
                    count +=1
            if message_list:
                return Response({"Lasted message":message_list.content,"new_message_count":count,"new_ms_room_count":message_list_not_read_all_room_count}, status=200)
        return Response({Message.SC_NOT_FOUND}, status=200)
    return Response({Message.SC_OK},status=200)

