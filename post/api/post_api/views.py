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
from post.models import Post, PositivePoint, Comment, View, PostType, PostPoint
from rest_framework.response import Response
from post.serializers import PostSerializer, PostTypeSerializer, PostGraphSerializer
from django.contrib.auth import get_user_model

from redditv1.message import Message

User = get_user_model()


@api_view(["GET"])
def post_list_view(request):
    top_community = Community.objects.filter(state=True).annotate(user_count=Count('user')).order_by(
        '-user_count')
    if request.user.is_authenticated:
        top_community = Community.objects.filter(user=request.user).union(
            Community.objects.filter(community__state=True)).distinct('community_type')
        # query = Post.objects.filter(user=request.user).union(Post.objects.filter(community__user=request.user)) \
        #     .union(Post.objects.filter(user__following=Profile.objects.filter(user=request.user).first())).union(
        #     Post.objects.filter(community__state=True, community__in=top_community).distinct().order_by('-postpoint__point'))
        # query = Post.objects.all().order_by('postpoint__point')
        query = Post.objects.filter(user=request.user).union(
            Post.objects.filter(community__user=request.user)).order_by('-point')
        return get_paginated_queryset_response(query, request)
    query = Post.objects.filter(community__state=True, community__in=top_community).order_by('-postpoint__point')
    return get_paginated_queryset_response(query, request)


@api_view(["GET", "POST"])
def post_create_api(request):
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
                _community = Community.objects.filter(community_type=community).first()
                positive_point = PositivePoint.objects.filter(user=user).first()
                positive_point.point = positive_point.point + 1
                positive_point.save()
                if image:
                    if len(image) > len('data:,'):
                        format, imgstr = image.split(';base64,')
                        ext = format.split('/')[-1]
                        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                        current_post = Post.objects.create(user=user, content=content, community=_community,
                                                           title=title,
                                                           type=PostType.objects.filter(type=type).first())
                        current_post.image = image
                        current_post.save()
                        serializer = PostSerializer(current_post)
                        return Response(serializer.data, status=201)
                current_post = Post.objects.create(user=user, content=content, community=_community, title=title,
                                                   type=PostType.objects.filter(type=type).first())
                PostPoint.objects.create(post=current_post)
                serializer = PostSerializer(current_post)
                return Response(serializer.data, status=201)
        return Response({Message.SC_BAD_RQ}, status=400)


@api_view(["POST"])
def post_delete_api(request, post_id):
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    post = Post.objects.filter(id=post_id)
    if not post:
        return Response({Message.SC_NOT_FOUND}, status=400)
    if not Post.objects.filter(user=request.user, id=post_id):
        return Response({Message.SC_PERMISSION_DENIED}, status=401)
    post.delete()
    return Response({Message.SC_OK}, status=200)


@api_view(["GET"])
def post_find_by_id(request, post_id):
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
            if Community.objects.filter(user=request.user, community_type=post.community):
                serializer = check_view(view, post, request.user)
                return Response(serializer.data, status=200)
            return Response({Message.MUST_FOLLOW}, status=400)
    return Response({Message.SC_NOT_FOUND}, status=204)


@api_view(["POST", "GET"])
def re_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    post = Post.objects.filter(id=post_id).first()
    if post:
        new_post = Post.objects.create(parent=post, user=request.user)
        serializer = PostSerializer(new_post)
        return Response(serializer.data, status=200)
    return Response({Message.SC_NOT_FOUND}, status=204)


@api_view(["POST"])
def post_action(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    post_id = request.data.get('id')
    action = request.data.get('action')
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({Message.SC_NOT_FOUND}, status=204)
    if action:
        positive_point = PositivePoint.objects.filter(user=request.user).first()
        if action == "up_vote":
            if Post.objects.filter(id=post_id, up_vote=request.user):
                post.up_vote.remove(request.user)
                positive_point.point = positive_point.point - 2
                positive_point.save()
                post_point = PostPoint.objects.filter(post=post).first()
                post_point.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                            datetime.datetime.now())
                return Response({Message.SC_OK}, status=200)
            post.up_vote.add(request.user)
            post.down_vote.remove(request.user)
            positive_point.point = positive_point.point + 2
            positive_point.save()
            post_point = PostPoint.objects.filter(post=post).first()
            post_point.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                        datetime.datetime.now())
            return Response({Message.SC_OK}, status=200)
        if action == "down_vote":
            if Post.objects.filter(id=post_id, down_vote=request.user):
                post.down_vote.remove(request.user)
                positive_point.point = positive_point.point + 2
                positive_point.save()
                post_point = PostPoint.objects.filter(post=post).first()
                post_point.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                            datetime.datetime.now())
                return Response({Message.SC_OK}, status=200)
            post.down_vote.add(request.user)
            post.up_vote.remove(request.user)
            positive_point.point = positive_point.point - 2
            positive_point.save()
            post_point = PostPoint.objects.filter(post=post).first()
            post_point.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                        datetime.datetime.now())
            return Response({Message.SC_OK}, status=200)
    return Response({Message.SC_BAD_RQ}, status=400)


@api_view(["GET"])
def user_post(request):
    if request.user.is_authenticated:
        query = Post.objects.filter(user=request.user)
        return get_paginated_queryset_response(query, request)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def user_post_filter_by_up_vote(request):
    if request.user.is_authenticated:
        query = Post.objects.filter(user=request.user).annotate(
            user_count=Count("up_vote")
        ).order_by(
            "-user_count"
        ).filter(community__user=request.user)
        return get_paginated_queryset_response(query, request)
    return Response({Message.SC_NO_AUTH}, status=401)


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


def count_post_by_community(community):
    count = 0
    if Post.objects.filter(community__community_type=community):
        count = Post.objects.filter(community__community_type=community).count()
    return count


def get_paginated_queryset_response(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PostSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


def get_paginated_queryset_response_5(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 5
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PostSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


def get_paginated_queryset_response_post_type(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 5
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PostTypeSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def filter_by_up_vote(request):
    query = Post.objects.annotate(
        user_count=Count("up_vote")
    ).order_by(
        "-user_count"
    ).filter(community__state=True)
    return get_paginated_queryset_response(query, request)


@api_view(["GET"])
def get_post_by_comment(request):
    if request.user.is_authenticated:
        # level 1
        comment_list = Comment.objects.filter(user=request.user, parent__isnull=True)
        # level 2 + 3
        comment_list_level_3 = Comment.objects.filter(parent__isnull=False).filter(parent__parent__isnull=False).filter(
            parent__parent__parent__isnull=True, user=request.user)
        comment_list_level_2 = Comment.objects.filter(parent__isnull=False).filter(parent__parent__isnull=True,
                                                                                   user=request.user)
        query = Post.objects.filter(comment__in=comment_list)
        query_2 = Post.objects.filter(comment__in=parent_comment(comment_list_level_2, 2))
        query_3 = Post.objects.filter(comment__in=parent_comment(comment_list_level_3, 3))
        query_result = (query | query_2 | query_3).distinct()
        return get_paginated_queryset_response(query_result, request)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_post_by_username_comment(request, username):
    # level 1
    comment_list = Comment.objects.filter(user__username=username, parent__isnull=True)
    # level 2 + 3
    comment_list_level_3 = Comment.objects.filter(parent__isnull=False).filter(parent__parent__isnull=False).filter(
        parent__parent__parent__isnull=True, user__username=username)
    comment_list_level_2 = Comment.objects.filter(parent__isnull=False).filter(parent__parent__isnull=True,
                                                                               user__username=username)
    query = Post.objects.filter(comment__in=comment_list)
    query_2 = Post.objects.filter(comment__in=parent_comment(comment_list_level_2, 2))
    query_3 = Post.objects.filter(comment__in=parent_comment(comment_list_level_3, 3))
    query_result = (query | query_2 | query_3).distinct()
    return get_paginated_queryset_response(query_result, request)


@api_view(["GET"])
def find_post_by_user(request, username):
    post = Post.objects.filter(user__username=username, community__state=True)
    if post:
        return get_paginated_queryset_response(post, request)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET"])
def count_post_by_user(request, username):
    print("count", username)
    count = Post.objects.filter(user__username=username).count()
    print("count", username)
    if count:
        return Response({"Total": count}, status=200)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET"])
def find_post_by_up_vote(request):
    if request.user.is_authenticated:
        post = Post.objects.filter(up_vote=request.user)
        if post:
            return get_paginated_queryset_response(post, request)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


@api_view(["GET"])
def find_post_by_username_up_vote(request, username):
    if request.user.is_authenticated:
        no_block = Post.objects.filter(up_vote__username=username, community__user=request.user)
        if no_block:
            return get_paginated_queryset_response(no_block, request)
        return Response({Message.SC_NOT_FOUND}, status=400)
    post = Post.objects.filter(up_vote__username=username, community__state=True)
    if post:
        return get_paginated_queryset_response(post, request)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET"])
def find_post_by_down_vote(request):
    if request.user.is_authenticated:
        post = Post.objects.filter(down_vote=request.user)
        if post:
            return get_paginated_queryset_response(post, request)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


@api_view(["GET"])
def find_post_by_username_down_vote(request, username):
    if request.user.is_authenticated:
        no_block = Post.objects.filter(down_vote__username=username, community__user=request.user)
        if no_block:
            return get_paginated_queryset_response(no_block, request)
        return Response({Message.SC_NOT_FOUND}, status=400)
    post = Post.objects.filter(down_vote__username=username, community__state=True)
    if post:
        return get_paginated_queryset_response(post, request)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(['GET'])
def trending(request, days):
    if days:
        past = timestamp_in_the_past_by_day(days)
        post = Post.objects.filter(community__state=True, timestamp__gte=past,
                                   timestamp__lte=datetime.datetime.now()).annotate(
            user_count=Count("up_vote")
        ).order_by('-user_count')
        return get_paginated_queryset_response_5(post, request)
    post = Post.objects.filter(community__state=True).annotate(
        user_count=Count("up_vote")
    ).order_by('-user_count')
    return get_paginated_queryset_response_5(post, request)


@api_view(['GET'])
def hot(request):
    post = Post.objects.filter(community__state=True, timestamp__gte=timestamp_in_the_past_by_day(1),
                               timestamp__lte=datetime.datetime.now()).order_by('-postpoint__point')
    return get_paginated_queryset_response_5(post, request)


@api_view(['GET'])
def recent(request):
    post = Post.objects.filter(community__state=True).order_by('-timestamp')
    return get_paginated_queryset_response_5(post, request)


@api_view(['GET'])
def get_type_list(request):
    query = PostType.objects.all()
    return get_paginated_queryset_response_post_type(query, request)


def parent_comment(comment_list, level):
    comments = []
    if level == 3:
        for level_3 in comment_list:
            comments.append(level_3.parent.parent)
    if level == 2:
        for level_2 in comment_list:
            comments.append(level_2.parent)
    return comments


@api_view(["POST", "GET"])
def get_post_by_time_interval(request):
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    page_size = request.data.get('page_size')
    if from_timestamp is not None and to_timestamp is not None:
        query = Post.objects.filter(timestamp__gte=from_timestamp, timestamp__lte=to_timestamp, user=request.user)
        return get_paginated_queryset_response_graph(query, request, page_size)
    query = Post.objects.filter(timestamp__gte=timestamp_in_the_past_by_day(30), timestamp__lte=timezone.now(),
                                user=request.user)
    return get_paginated_queryset_response_graph(query, request, page_size)


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


def get_paginated_queryset_response_graph(query_set, request, page_size):
    paginator = PageNumberPagination()
    if page_size:
        paginator.page_size = page_size
    else:
        paginator.page_size = 50
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PostGraphSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


def timestamp_in_the_past_by_day(days):
    return timezone.now() - datetime.timedelta(days)


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
    if view.old_timestamp is not None:
        difference = (timezone.now() - view.old_timestamp).total_seconds()
        if difference >= 120:
            post.view_count = post.view_count + 1
            view.old_timestamp = timezone.now()
            view.save()
            post.save()
        serializer = PostSerializer(post)
        return serializer
