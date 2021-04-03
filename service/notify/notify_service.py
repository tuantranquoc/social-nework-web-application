from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from post import rank
from post.models import Post, Comment, CommentPoint
from rest_framework.response import Response
from notify.serializers import SignalRoomSerializer
from redditv1.message import Message
from function.paginator import get_paginated_queryset_response
from redditv1.name import ModelName, CommentState
from service.post.post_service import timestamp_in_the_past_by_day
from notify.models import SignalRoom, Notification, NotificationChange, NotificationObject, UserNotify
from django.contrib.auth import get_user_model
from django.db.models import Q
from function.paginator import get_paginated_queryset_response
User = get_user_model()


def get_signal_room(request):
    if request.user.is_authenticated:
        page_size = 1
        room = SignalRoom.objects.filter(user=request.user)
        if room:
            return get_paginated_queryset_response(room, request, page_size,
                                               ModelName.SIGNAL_ROOM)
    return Response(Message.SC_NO_AUTH, status=401)

def get_notify_list(request):
    if request.user.is_authenticated:
        user= request.user
        notify_list = Notification.objects.filter(user_notify__user=request.user)
        if notify_list:
            return get_paginated_queryset_response(notify_list, request, 15, ModelName.NOTIFICATION)
        return Response(Message.SC_NOT_FOUND,status=200)
    return Response(Message.SC_NO_AUTH, status=401)


def change_notify_status(request):
    if request.user.is_authenticated:
        user = request.user
        notification_id = request.data.get("id")
        notification = Notification.objects.filter(pk=notification_id).first()
        if notification:
            user_notify = notification.user_notify.all().filter(user=user).first()
            if user_notify:
                user_notify.status = 1
                user_notify.save()
                return Response(Message.SC_OK, status=200)
        return Response(Message.SC_BAD_RQ,status=400)
    return Response(Message.SC_NO_AUTH, status=401)


def change_notify_status_01(request):
    if request.user.is_authenticated:
        user = request.user
        user_notify_id = request.data.get("id")
        if user_notify_id:
            user_notify = UserNotify.objects.filter(pk=user_notify_id).first()
            if user_notify:
                user_notify.status = 1
    return Response(Message.SC_NO_AUTH, status=401)
