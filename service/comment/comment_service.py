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


def comment_parent_list(request, comment_id, *args, **kwargs):
    sort = request.data.get("sort")
    page_size = request.data.get("page_size")
    comment = Comment.objects.filter(parent__id=comment_id)
    if sort:
        comment.order_by('-up_vote')
    else:
        comment.order_by('-commentpoint__point')
    return get_paginated_queryset_response(comment, request, page_size,
                                           ModelName.COMMENT)


def child_comment_create(request, comment_id):
    """
    data = {"content":"CONTENT"}
    """
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        comment = Comment.objects.filter(id=comment_id).first()
        if not comment:
            return Response({Message.SC_BAD_RQ}, status=204)
        content = request.data.get("content")
        comment = Comment.objects.create(parent=comment,
                                         content=content,
                                         user=request.user)
        CommentPoint.objects.create(comment=comment)
        if comment:
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=201)
        return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_NO_AUTH}, status=401)


def comment_create(request):
    if request.user.is_authenticated:
        content = request.data.get("content")
        post_id = request.data.get("id")
        if content and post_id:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(user=request.user,
                                             post=post,
                                             content=content)
            CommentPoint.objects.create(comment=comment)
            comment = Comment.objects.filter(id=comment.id)
            serializer = CommentSerializer(comment, many=True)
            return Response(serializer.data, status=201)
    else:
        return Response({Message.SC_NO_AUTH}, status=403)


def get_list_comment_level_1_by_post(request, post_id):
    page_size = request.data.get("page_size")
    comment = Comment.objects.filter(
        post_id=post_id).order_by('-commentpoint__point')
    return get_paginated_queryset_response(comment, request, page_size,
                                           ModelName.COMMENT)


def comment_action(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    comment_id = request.data.get('id')
    action = request.data.get('action')
    if comment_id:
        comment = Comment.objects.filter(id=comment_id).first()
        if action == "up_vote":
            comment.up_vote.add(request.user)
            comment.down_vote.remove(request.user)
            comment_point_update(comment)
            return Response(Message.SC_OK, status=200)
        if action == "down_vote":
            comment.up_vote.remove(request.user)
            comment.down_vote.add(request.user)
            comment_point_update(comment)
            return Response(Message.SC_OK, status=200)
    return Response(Message.SC_BAD_RQ, status=400)


def check_vote(request):
    if request.user.is_authenticated:
        comment_id = request.data.get('id')
        if Comment.objects.filter(up_vote=request.user, id=comment_id):
            return Response({"up_vote"})
        if Comment.objects.filter(down_vote=request.user, id=comment_id):
            return Response({"down_vote"})
    return Response({"none"})


def comment_point_update(comment):
    if comment:
        comment_point = CommentPoint.objects.filter(comment=comment).first()
        comment_point.point = rank.confidence(comment.up_vote.count(),
                                              comment.down_vote.count())
        comment_point.save()


def filter_by_up_vote(request):
    page_size = request.data.get("page_size")
    query = Comment.objects.annotate(
        user_count=Count("up_vote")).order_by("-user_count")
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.COMMENT)


def count_comment_by_post(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if post:
        comment_list = Comment.objects.filter(post=post)
        return Response({"Total": loop_comment(comment_list, True)},
                        status=200)
    return Response({Message.SC_BAD_RQ}, status=400)


def loop_comment(comment_list, flag):
    count = 0
    if flag:
        count += comment_list.count()
    if comment_list:
        for c in comment_list:
            comment_list_with_parent_c = Comment.objects.filter(parent=c)
            if comment_list_with_parent_c:
                count += comment_list_with_parent_c.count()
                count += loop_comment(comment_list_with_parent_c, False)
    return count


def get_comment_by_id(request, comment_id):
    comment = Comment.objects.filter(id=comment_id).first()
    if comment:
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=200)
    return Response(Message.SC_BAD_RQ, status=400)


def get_comment_by_time_interval(request):
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    page_size = request.data.get('page_size')
    if from_timestamp is not None and to_timestamp is not None:
        query = Comment.objects.filter(timestamp__gte=from_timestamp,
                                       timestamp__lte=to_timestamp,
                                       user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.COMMENT_GRAPH)
    query = Comment.objects.filter(
        timestamp__gte=timestamp_in_the_past_by_day(30),
        timestamp__lte=timezone.now(),
        user=request.user)
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.COMMENT_GRAPH)


def count_post_by_user(request, username):
    comment = Comment.objects.filter(user__username=username)
    if comment:
        return Response({"Total": comment.count()}, status=200)
    return Response({Message.SC_NOT_FOUND}, status=400)


def reset(request):
    query = Comment.objects.all()
    for comment in query:
        # comment_point = CommentPoint.objects.filter(comment=comment)
        # if not comment_point:
        #     CommentPoint.objects.create(comment=comment,
        #                                 point=rank.confidence(comment.up_vote.count(), comment.down_vote.count()))
        comment.point = rank.confidence(comment.up_vote.count(),
                                        comment.down_vote.count())
        comment.save()
    return Response({Message.SC_OK}, status=200)