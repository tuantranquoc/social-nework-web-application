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
from redditv1.name import ModelName
from service.post.post_service import timestamp_in_the_past_by_day
from service.comment import comment_service


@api_view(['GET', 'POST'])
def comment_parent_list_view(request, comment_id):
    return comment_service.comment_parent_list(request, comment_id)


@api_view(['POST'])
def child_comment_create_view(request, comment_id):
    """
    data = {"content":"CONTENT"}
    """
    return comment_service.child_comment_create(request, comment_id)


@api_view(['POST'])  # http method client has send == POST
def comment_create_view(request):
    """
    data = {"id":"comment_id","content":"content"}
    """
    return comment_service.comment_create(request)


@api_view(['GET'])  # http method client has send == POST
def comment_api_view(request, post_id, *args, **kwargs):
    return comment_service.get_list_comment_level_1_by_post(request, post_id)


@api_view(['POST'])
def comment_action(request):
    return comment_service.comment_action(request)


@api_view(["GET"])
def get_comment_by_id(request, comment_id):
    return comment_service.get_comment_by_id(request, comment_id)


@api_view(["POST"])
def check_vote(request):
    return comment_service.check_vote(request)


@api_view(["GET"])
def filter_by_up_vote(request):
    return comment_service.filter_by_up_vote(request)


@api_view(["GET"])
def count_comment_by_post(request, post_id):
    return comment_service.count_comment_by_post(request, post_id)


@api_view(["GET"])
def count_by_user_post(request, username):
    return comment_service.count_post_by_user(request, username)


@api_view(["POST", "GET"])
def get_comment_by_time_interval(request):
    return comment_service.get_comment_by_time_interval(request)


@api_view(["GET"])
def reset(request):
    return comment_service.reset(request)

@api_view(["GET","POST"])
def update_comment_level(request):
    return comment_service.update_comment_level(request)


