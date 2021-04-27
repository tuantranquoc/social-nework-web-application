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
    """
    ``NOTE should change this``
    
    ``GET`` Return list of comment by provided ``COMMENT_ID``.

    **Example post request**:
    .. code-block:: json

        {
            "page_size": "5",
            "sort":"up_vote"
        }
    """
    return comment_service.comment_parent_list(request, comment_id)


@api_view(['POST'])
def child_comment_create_view(request, comment_id):
    """
    ``NOTE should change this``
    
    ``GET`` Create child comment based on provided ``COMMENT_ID``.

    **Example post request**:
    .. code-block:: json

        {
            "content":"hello world"
        }
    """
    return comment_service.child_comment_create(request, comment_id)


@api_view(['POST'])  # http method client has send == POST
def comment_create_view(request):
    """
    ``GET`` Create comment based on provided ``POST_ID``.

    **Example post request**:
    .. code-block:: json

        {
            "id":"post_id",
            "content":"hello world"
        }
    """
    return comment_service.comment_create(request)


@api_view(['POST'])
def delete_comment(request):
    """
    ``POST`` Delete comment based on provided ``COMMENT_ID``.

    **Example post request**:
    .. code-block:: json

        {
            "page_size":"5"
        }
    """
    return comment_service.delete_comment(request)


@api_view(['GET'])  # http method client has send == POST
def comment_api_view(request, post_id, *args, **kwargs):
    """
    ``GET`` Return list comment ``level 1`` based on provided ``POST_ID``.

    **Example post request**:
    .. code-block:: json

        {
            "id":"comment_id"
        }
    """
    return comment_service.get_list_comment_level_1_by_post(request, post_id)


@api_view(['POST'])
def comment_action(request):
    """
    ``POST`` up_vote or down_vote comment.

    ``action`` has 2 type ``up_vote`` and ``down_vote``

    **Example post request**:
    .. code-block:: json

        {
            "id":"comment_id",
            "action":"up_vote"
        }
    """
    return comment_service.comment_action(request)


@api_view(["GET"])
def get_comment_by_id(request, comment_id):
    """
    ``GET`` Return comment by provied ``COMMENT_ID``.
    """
    return comment_service.get_comment_by_id(request, comment_id)


@api_view(["POST"])
def check_vote(request):
    """
    ``POST`` Check current vote on provied ``COMMENT_ID`` by current user.
    """
    return comment_service.check_vote(request)


@api_view(["GET"])
def filter_by_up_vote(request):
    """
    ``GET`` Return list of comment filter by ``up_vote``.
    """
    return comment_service.filter_by_up_vote(request)


@api_view(["GET"])
def count_comment_by_post(request, post_id):
    """
    ``GET`` Return total number of comment by ``POST_ID``.
    """
    return comment_service.count_comment_by_post(request, post_id)


@api_view(["GET"])
def count_by_user_post(request, username):
    """
    ``GET`` Return total number of post by ``USER``.
    """
    return comment_service.count_post_by_user(request, username)


@api_view(["POST", "GET"])
def get_comment_by_time_interval(request):
    return comment_service.get_comment_by_time_interval(request)


@api_view(["GET"])
def reset(request):
    return comment_service.reset(request)


@api_view(["GET", "POST"])
def update_comment_level(request):
    return comment_service.update_comment_level(request)

@api_view(["GET"])
def count_comment_by_comment_parent(request, comment_id):
    """
    ``GET`` Return total number of comment by ``COMMENT_PARENT``.
    """
    return comment_service.count_comment_by_comment_parent(request, comment_id)
