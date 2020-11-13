from community.models import Community
from django.db.models.aggregates import Count
from function.paginator import get_paginated_queryset_response
from post.models import Comment, PositivePoint, Post, PostType, View
from account.models import Profile
from redditv1.name import ModelName
from rest_framework.response import Response
from redditv1.message import Message
from function.file import get_image
from post import rank
from post.serializers import PostSerializer
from django.utils import timezone
import datetime


def count_post_by_community(community):
    count = 0
    if Post.objects.filter(community__community_type=community):
        count = Post.objects.filter(
            community__community_type=community).count()
    return count


def timestamp_in_the_past_by_day(days):
    return timezone.now() - datetime.timedelta(days)


def parent_comment(comment_list, level):
    comments = []
    if level == 3:
        for level_3 in comment_list:
            comments.append(level_3.parent.parent)
    if level == 2:
        for level_2 in comment_list:
            comments.append(level_2.parent)
    return comments


def get_post_list(request):
    sort = request.data.get("sort")
    page_size = request.data.get("page_size")
    # this algorithm
    if not sort:
        sort = '-point'
    if sort == 'timestamp':
        sort = '-timestamp'
    top_community = Community.objects.filter(state=True).annotate(
        user_count=Count('user')).order_by('-user_count')
    if request.user.is_authenticated:
        top_community = Community.objects.filter(user=request.user).union(
            Community.objects.filter(community__state=True)).union(
                Community.objects.filter(creator=request.user)).distinct()
        query = Post.objects.filter(user=request.user).union(
            Post.objects.filter(community__user=request.user)).union(
                Post.objects.filter(user__following=Profile.objects.filter(
                    user=request.user).first())).union(
                        Post.objects.filter(community__state=True).distinct()
                    ).distinct().order_by(sort)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    query = Post.objects.filter(community__state=True,
                                community__in=top_community)
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.POST)


def create_post(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    if request.method == "POST":
        title = request.data.get("title")
        content = request.data.get("content")
        community = request.data.get("community")
        image = request.data.get('image')
        type = request.data.get('type')
        if community is None:
            return Response({Message.SC_BAD_RQ}, status=400)
        user = request.user
        if community:
            if Community.objects.filter(community_type=community):
                _community = Community.objects.filter(
                    community_type=community).first()
                positive_point = PositivePoint.objects.filter(
                    user=user).first()
                positive_point.point = positive_point.point + 1
                positive_point.save()
                if image:
                    if len(image) > len('data:,'):
                        current_post = Post.objects.create(
                            user=user,
                            content=content,
                            community=_community,
                            title=title,
                            type=PostType.objects.filter(type=type).first())
                        current_post.image = get_image(image)
                        current_post.point = rank.hot(0, 0,
                                                      current_post.timestamp)
                        current_post.save()
                        serializer = PostSerializer(current_post)
                        return Response(serializer.data, status=201)
                current_post = Post.objects.create(
                    user=user,
                    content=content,
                    community=_community,
                    title=title,
                    type=PostType.objects.filter(type=type).first())
                current_post.point = rank.hot(0, 0, current_post.timestamp)
                current_post.save()
                serializer = PostSerializer(current_post)
                return Response(serializer.data, status=201)
        return Response({Message.SC_BAD_RQ}, status=400)


def delete_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    post = Post.objects.filter(id=post_id)
    if not post:
        return Response({Message.SC_NOT_FOUND}, status=400)
    if not Post.objects.filter(user=request.user, id=post_id):
        return Response({Message.SC_PERMISSION_DENIED}, status=401)
    post.delete()
    return Response({Message.SC_OK}, status=200)


def find_post_by_id(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if post:
        if post.community.state is True:
            if not request.user.is_authenticated:
                serializer = PostSerializer(post)
                return Response(serializer.data, status=200)
            if post.user == request.user:
                serializer = PostSerializer(post)
                return Response(serializer.data, status=200)
            view = View.objects.filter(user=request.user, post=post).first()
            serializer = check_view(view, post, request.user)
            return Response(serializer.data, status=200)
        if post.community.state is False:
            if not request.user.is_authenticated:
                return Response({Message.SC_LOGIN_REDIRECT}, status=401)
            view = View.objects.filter(user=request.user, post=post).first()
            if Community.objects.filter(user=request.user,
                                        community_type=post.community):
                serializer = check_view(view, post, request.user)
                return Response(serializer.data, status=200)
            return Response({Message.MUST_FOLLOW}, status=400)
    return Response({Message.SC_NOT_FOUND}, status=204)


def check_view(view, post, user):
    if not view:
        view = View.objects.create(post=post)
        view.user.add(user)
        view.save()
    if view.old_timestamp is None:
        view.old_timestamp = timezone.now()
        view.save()
        post.view_count = post.view_count + 1
        post.save()
        serializer = PostSerializer(post)
        return serializer
    if view.old_timestamp is not None:
        difference = (timezone.now() - view.old_timestamp).total_seconds()
        if difference >= 120:
            post.view_count = post.view_count + 1
            view.old_timestamp = timezone.now()
            view.save()
            post.save()
        serializer = PostSerializer(post)
        return serializer


def re_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    post = Post.objects.filter(id=post_id).first()
    if post:
        new_post = Post.objects.create(parent=post, user=request.user)
        serializer = PostSerializer(new_post)
        return Response(serializer.data, status=200)
    return Response({Message.SC_NOT_FOUND}, status=204)


def action(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    post_id = request.data.get('id')
    action = request.data.get('action')
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({Message.SC_NOT_FOUND}, status=204)
    if action:
        positive_point = PositivePoint.objects.filter(
            user=request.user).first()
        if not positive_point:
            positive_point = PositivePoint.objects.create(user=request.user)
        if action == "up_vote":
            if Post.objects.filter(id=post_id, up_vote=request.user):
                post.up_vote.remove(request.user)
                positive_point.point = positive_point.point - 2
                positive_point.save()
                post.point = rank.hot(post.up_vote.count(),
                                      post.down_vote.count(), post.timestamp)
                post.save()
                return Response({Message.SC_OK}, status=200)
            post.up_vote.add(request.user)
            post.down_vote.remove(request.user)
            positive_point.point = positive_point.point + 2
            positive_point.save()
            post.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                  post.timestamp)
            post.save()
            return Response({Message.SC_OK}, status=200)
        if action == "down_vote":
            if Post.objects.filter(id=post_id, down_vote=request.user):
                post.down_vote.remove(request.user)
                positive_point.point = positive_point.point + 2
                positive_point.save()
                post.point = rank.hot(post.up_vote.count(),
                                      post.down_vote.count(), post.timestamp)
                post.save()
                return Response({Message.SC_OK}, status=200)
            post.down_vote.add(request.user)
            post.up_vote.remove(request.user)
            positive_point.point = positive_point.point - 2
            positive_point.save()
            post.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                  post.timestamp)
            post.save()
            return Response({Message.SC_OK}, status=200)
    return Response({Message.SC_BAD_RQ}, status=400)


def find_post_by_user(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        query = Post.objects.filter(user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)


def find_post_by_up_vote(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        query = Post.objects.filter(user=request.user).annotate(
            user_count=Count("up_vote")).order_by("-user_count").filter(
                community__user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)


def find_post_by_community(request, community_type):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(community__community_type=community_type)
    community = Community.objects.filter(community_type=community_type).first()
    if not community:
        return Response({Message.SC_NOT_FOUND}, status=204)
    if request.user.is_authenticated:
        if community.state == True:
            return get_paginated_queryset_response(post, request, page_size,
                                                   ModelName.POST)
        post = post.filter(user=request.user)
        if post:
            return get_paginated_queryset_response(post, request, page_size,
                                                   ModelName.POST)
        return Response({Message.MUST_FOLLOW}, status=403)
    if community.state == False:
        return Response({Message.MUST_FOLLOW}, status=403)
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def find_post_by_comment(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        # level 1
        comment_list = Comment.objects.filter(user=request.user,
                                              parent__isnull=True)
        # level 2 + 3
        comment_list_level_3 = Comment.objects.filter(
            parent__isnull=False).filter(parent__parent__isnull=False).filter(
                parent__parent__parent__isnull=True, user=request.user)
        comment_list_level_2 = Comment.objects.filter(
            parent__isnull=False).filter(parent__parent__isnull=True,
                                         user=request.user)
        query = Post.objects.filter(comment__in=comment_list)
        query_2 = Post.objects.filter(
            comment__in=parent_comment(comment_list_level_2, 2))
        query_3 = Post.objects.filter(
            comment__in=parent_comment(comment_list_level_3, 3))
        query_result = (query | query_2 | query_3).distinct()
        return get_paginated_queryset_response(query_result, request,
                                               page_size, ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)


def find_post_by_comment_with_username(request, username):
    page_size = request.data.get("page_size")
    # level 1
    comment_list = Comment.objects.filter(user__username=username,
                                          parent__isnull=True)
    # level 2 + 3
    comment_list_level_3 = Comment.objects.filter(parent__isnull=False).filter(
        parent__parent__isnull=False).filter(
            parent__parent__parent__isnull=True, user__username=username)
    comment_list_level_2 = Comment.objects.filter(parent__isnull=False).filter(
        parent__parent__isnull=True, user__username=username)
    query = Post.objects.filter(comment__in=comment_list)
    query_2 = Post.objects.filter(
        comment__in=parent_comment(comment_list_level_2, 2))
    query_3 = Post.objects.filter(
        comment__in=parent_comment(comment_list_level_3, 3))
    query_result = (query | query_2 | query_3).distinct()
    return get_paginated_queryset_response(query_result, request, page_size,
                                           ModelName.POST)


def find_post_by_down_vote(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        post = Post.objects.filter(down_vote=request.user)
        if post:
            return get_paginated_queryset_response(post, request, page_size,
                                                   ModelName.POST)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


# def find_post_by_comment(request):


def find_post_by_username_down_vote(request, username):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        no_block = Post.objects.filter(down_vote__username=username,
                                       community__user=request.user)
        if no_block:
            return get_paginated_queryset_response(no_block, request,
                                                   page_size, ModelName.POST)
        return Response({Message.SC_NOT_FOUND}, status=400)
    post = Post.objects.filter(down_vote__username=username,
                               community__state=True)
    if post:
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NOT_FOUND}, status=400)


def find_post_by_username_up_vote(request, username):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        no_block = Post.objects.filter(up_vote__username=username,
                                       community__user=request.user)
        if no_block:
            return get_paginated_queryset_response(no_block, request,
                                                   page_size, ModelName.POST)
        return Response({Message.SC_NOT_FOUND}, status=400)
    post = Post.objects.filter(up_vote__username=username,
                               community__state=True)
    if post:
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NOT_FOUND}, status=400)


def trending(request, days):
    page_size = request.data.get("page_size")
    if days:
        past = timestamp_in_the_past_by_day(days)
        post = Post.objects.filter(
            community__state=True,
            timestamp__gte=past,
            timestamp__lte=datetime.datetime.now()).annotate(
                user_count=Count("up_vote")).order_by('-user_count')
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    post = Post.objects.filter(community__state=True).annotate(
        user_count=Count("up_vote")).order_by('-user_count')
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def hot(request):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(
        community__state=True,
        timestamp__gte=timestamp_in_the_past_by_day(1),
        timestamp__lte=datetime.datetime.now()).order_by('-point')
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def find_post_by_up_vote(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        post = Post.objects.filter(up_vote=request.user)
        if post:
            return get_paginated_queryset_response(post, request, page_size,
                                                   ModelName.POST)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


def recent(request):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(community__state=True).order_by('-timestamp')
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def get_post_by_time_interval(request):
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    page_size = request.data.get('page_size')
    if from_timestamp is not None and to_timestamp is not None:
        query = Post.objects.filter(timestamp__gte=from_timestamp,
                                    timestamp__lte=to_timestamp,
                                    user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST,
                                               ModelName.POST_GRAPH)
    query = Post.objects.filter(
        timestamp__gte=timestamp_in_the_past_by_day(30),
        timestamp__lte=timezone.now(),
        user=request.user)
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.POST_GRAPH)
    
    