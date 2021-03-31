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
from notify.models import SignalRoom
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