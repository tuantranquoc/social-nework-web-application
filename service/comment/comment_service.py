from django.db.models import Count, Q
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
from notify.models import Notification, NotificationChange, NotificationObject, EntityType, UserNotify
from functools import reduce
import operator
from community.models import Member, MemberInfo
from account.models import Profile


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
        parent = Comment.objects.filter(id=comment_id).first()
        if not parent:
            return Response({Message.SC_BAD_RQ}, status=204)
        content = request.data.get("content")
        level = parent.level
        if content:
            if level < 6:
                level += 1
            else:
                parent = parent.parent
            comment = Comment.objects.create(parent=parent,
                                             content=content,
                                             user=request.user,
                                             level=level)
            CommentPoint.objects.create(comment=comment)
            if comment:
                serializer = CommentSerializer(comment)
                return Response(serializer.data, status=201)
            return Response({Message.SC_BAD_RQ}, status=400)
        return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_NO_AUTH}, status=401)


def handle_notification(post, source_user):
    entity_type = EntityType.objects.filter(id=6).first()
    notification_object = NotificationObject.objects.create(
        entity_type=entity_type, post=post)
    notifycation_change = NotificationChange.objects.create(
        user=post.user, notification_object=notification_object)
    notification = Notification.objects.create()
    user_notify = UserNotify.objects.create(user=post.user)
    user_notify.notification_object.add(notification_object)
    message = "User " + source_user.username + " has created a comment to your post"
    user_notify.message = message
    user_notify.save()
    print(user_notify.message)
    notification.user_notify.add(user_notify)
    notification.save()



def comment_create(request):
    if request.user.is_authenticated:
        content = request.data.get("content")
        post_id = request.data.get("id")
        if content and post_id:
            post = Post.objects.get(id=post_id)
            user = post.user
            comment = Comment.objects.create(user=request.user,
                                             post=post,
                                             content=content)
            handle_notification(post, request.user)
            # if comment:
            #     entity_type = EntityType.objects.filter(id=4).first()
            #     notification_object = NotificationObject.objects.create(
            #         entity_type=entity_type, post=post)
            #     notifycation_change = NotificationChange.objects.create(
            #         user=request.user, notification_object=notification_object)
            #     user_notify = UserNotify.objects.create(user=user)
            #     notification = Notification.objects.create(
            #         notification_object=notification_object)
            #     notification.user_notify.add(user_notify)
            #     notification.save()
            CommentPoint.objects.create(comment=comment)
            comment = Comment.objects.filter(id=comment.id)
            serializer = CommentSerializer(comment, many=True)
            return Response(serializer.data, status=201)
        return Response({Message.DETAIL: Message.SC_BAD_RQ}, status=201)
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
        return Response({"Total": comment_count(comment_list, True)},
                        status=200)
    return Response({Message.SC_BAD_RQ}, status=400)


def comment_count(comment_list, flag):
    count = 0
    if flag:
        count += comment_list.count()
    if comment_list:
        for c in comment_list:
            comment_list_with_parent_c = Comment.objects.filter(parent=c)
            if comment_list_with_parent_c:
                count += comment_list_with_parent_c.count()
                count += comment_count(comment_list_with_parent_c, False)
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
        comment.point = rank.confidence(comment.up_vote.count(),
                                        comment.down_vote.count())
        comment.save()
    return Response({Message.SC_OK}, status=200)


# these function suppos to update level comment only
def update_comment_level(request):
    post = Post.objects.all()
    for p in post:
        comment = Comment.objects.filter(post=p)
        update_level_test_only(comment, 1)
    return Response({Message.DETAIL: Message.SC_OK}, status=200)


def update_level_test_only(comment_list, level):
    print(level, 'level')
    if comment_list:
        for c in comment_list:
            comment_list_with_parent_c = Comment.objects.filter(parent=c)
            if comment_list_with_parent_c:
                level += 1
                print(level, comment_list_with_parent_c.values('id'))
                for c_ in comment_list_with_parent_c:
                    c_.level = level
                    c_.save()
                update_level_test_only(comment_list_with_parent_c, level)


def delete_comment(request):
    if request.user:
        if request.user.is_authenticated:
            id = request.data.get('id')
            comment = Comment.objects.filter(id=id).first()
            if comment:
                if comment.user == request.user:
                    child_list = Comment.objects.filter(parent=comment)
                    comment.state = CommentState.DELETED
                    comment.save()
                    return Response({Message.DETAIL: Message.SC_OK},
                                    status=200)
                post = find_post_by_comment(comment)
                if post:
                    if post.community.creator == request.user:
                        comment.state = CommentState.HIDDEN
                        comment.save()
                        return Response({Message.DETAIL: Message.SC_OK},
                                        status=200)
                return Response({Message.DETAIL: Message.SC_PERMISSION_DENIED},
                                status=401)
            return Response({Message.DETAIL: Message.SC_NOT_FOUND}, status=204)
        return Response({Message.DETAIL: Message.SC_NO_AUTH}, status=401)
    return Response({Message.DETAIL: Message.SC_BAD_RQ}, status=400)


def find_post_by_comment(comment):
    if comment:
        while comment.parent:
            comment = comment.parent
        return comment.post