import base64
import datetime
from django.core.files.base import ContentFile
from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from account.models import Profile
from community.models import Community
from post import rank
from post.models import Post, PositivePoint, Comment, View, PostType
from rest_framework.response import Response
from post.serializers import PostSerializer, PostTypeSerializer, PostGraphSerializer
from django.contrib.auth import get_user_model
from function.paginator import get_paginated_queryset_response
from function.file import get_image

from redditv1.message import Message
from redditv1.name import ModelName
from service.post import post_service

User = get_user_model()


@api_view(["GET", "POST"])
def post_list_view(request):
    return post_service.get_post_list(request)


@api_view(["GET", "POST"])
def post_create_api(request):
    return post_service.create_post(request)


@api_view(["POST"])
def post_delete_api(request, post_id):
    return post_service.delete_post(request, post_id)


@api_view(["GET"])
def find_post_by_id(request, post_id):
    return post_service.find_post_by_id(request, post_id)


@api_view(["POST", "GET"])
def re_post(request, post_id):
    return post_service.re_post(request, post_id)


@api_view(["POST"])
def post_action(request):
    return post_service.action(request)


@api_view(["GET"])
def get_list_post_by_user(request):
    return post_service.find_post_by_user(request)


@api_view(["GET"])
def get_list_post_by_up_vote(request):
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def user_comment_post(request):
    if request.user.is_authenticated:
        comment = Comment.objects.filter(user=request.user)
        # return get_paginated_queryset_response(query, request)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_community(request, community_type):
    return Response({"Total": count_post_by_community(community_type)})


@api_view(["GET"])
def get_post_count(request):
    count = Post.objects.filter(user=request.user).count()
    return Response({"Total": count})


@api_view(["GET"])
def get_comment_count(request):
    count = Comment.objects.filter(user=request.user).count()
    return Response({"Total": count})


@api_view(["GET"])
def get_count_by_vote(request):
    up_vote_count = Post.objects.filter(up_vote=request.user).count()
    down_vote_count = Post.objects.filter(down_vote=request.user).count()
    return Response({"Total": up_vote_count + down_vote_count})


@api_view(["GET"])
def get_count_by_up_vote(request):
    up_vote_count = Post.objects.filter(up_vote=request.user).count()
    return Response({"Total": up_vote_count})


@api_view(["GET"])
def get_count_by_username_up_vote(request, username):
    up_vote_count = Post.objects.filter(up_vote__username=username).count()
    return Response({"Total": up_vote_count})


@api_view(["GET"])
def get_count_by_down_vote(request):
    down_vote_count = Post.objects.filter(down_vote=request.user).count()
    return Response({"Total": down_vote_count})


@api_view(["GET"])
def get_count_by_username_down_vote(request, username):
    down_vote_count = Post.objects.filter(down_vote__username=username).count()
    return Response({"Total": down_vote_count})


@api_view(["GET"])
def get_count_by_user_vote(request, username):
    up_vote_count = Post.objects.filter(up_vote__username=username).count()
    down_vote_count = Post.objects.filter(down_vote__username=username).count()
    return Response({"Total": up_vote_count + down_vote_count})


@api_view(["POST"])
def check_vote(request):
    if request.user.is_authenticated:
        post_id = request.data.get('id')
        if Post.objects.filter(up_vote=request.user, id=post_id):
            return Response({"up_vote"})
        if Post.objects.filter(down_vote=request.user, id=post_id):
            return Response({"down_vote"})
    return Response({"none"})


@api_view(["GET", "POST"])
def filter_by_up_vote(request):
    page_size = request.data.get("page_size")
    query = Post.objects.annotate(
        user_count=Count("up_vote")).order_by("-user_count").filter(
            community__state=True)
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.POST)


@api_view(["GET"])
def get_post_by_comment(request):
    return post_service.find_post_by_comment(request)


@api_view(["GET"])
def get_post_by_username_comment(request, username):
    return post_service.find_post_by_comment_with_username(request, username)


@api_view(["GET"])
def find_post_by_user(request, username):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(user__username=username, community__state=True)
    if post:
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET"])
def count_post_by_user(request, username):
    count = Post.objects.filter(user__username=username).count()
    if count:
        return Response({"Total": count}, status=200)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET"])
def find_post_by_up_vote(request):
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def find_post_by_username_up_vote(request, username):
    return post_service.find_post_by_username_up_vote(request, username)


@api_view(["GET"])
def find_post_by_down_vote(request):
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def find_post_by_username_down_vote(request, username):
    return post_service.find_post_by_username_down_vote(request, username)


@api_view(['GET', 'POST'])
def trending(request, days):
    return post_service.trending(request, days)


@api_view(['GET', 'POST'])
def hot(request):
    return post_service.hot(request)


@api_view(['GET', 'POST'])
def recent(request):
    return post_service.recent(request)


@api_view(['GET'])
def get_type_list(request):
    page_size = request.data.get("page_size")
    query = PostType.objects.all()
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.POST_TYPE)


@api_view(["POST", "GET"])
def get_post_by_time_interval(request):
    return post_service.get_post_by_time_interval(request)


@api_view(["GET"])
def reset(request):
    # query = PostPoint.objects.all()
    # query.delete()
    post = Post.objects.all()
    for p in post:
        # post_point = PostPoint.objects.filter(post=p)
        # if not post_point:
        #     PostPoint.objects.create(post=p,
        #                              point=rank.hot(p.up_vote.count(), p.down_vote.count(), datetime.datetime.now()))
        p.point = rank.hot(p.up_vote.count(), p.down_vote.count(), p.timestamp)
        p.save()
    return Response({Message.SC_OK}, status=200)


@api_view(["GET", "POST"])
def find_post_by_community(request, community_type):
    return post_service.find_post_by_community(request, community_type)


def count_post_by_community(community):
    count = 0
    if Post.objects.filter(community__community_type=community):
        count = Post.objects.filter(
            community__community_type=community).count()
    return count


# def timestamp_in_the_past_by_day(days):
#     return timezone.now() - datetime.timedelta(days)

# def parent_comment(comment_list, level):
#     comments = []
#     if level == 3:
#         for level_3 in comment_list:
#             comments.append(level_3.parent.parent)
#     if level == 2:
#         for level_2 in comment_list:
#             comments.append(level_2.parent)
#     return comments
