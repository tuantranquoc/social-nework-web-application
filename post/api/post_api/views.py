from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from community.models import Community
from post.models import Post, PositivePoint, Comment
from rest_framework.response import Response
from post.serializers import PostSerializer
from django.contrib.auth import get_user_model

from redditv1.message import Message

User = get_user_model()


@api_view(["GET"])
def post_list_view(request):
    query = Post.objects.all()
    return get_paginated_queryset_response(query, request)


@api_view(["GET", "POST"])
def post_create_api(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    if request.method == "POST":
        content = request.data.get("content")
        community = request.data.get("community")
        if community is None:
            return Response({Message.SC_BAD_RQ}, status=400)
        user = request.user
        if content:
            if community:
                if Community.objects.filter(community_type=community):
                    _community = Community.objects.filter(community_type=community).first()
                    _community = Community.objects.filter(community_type=community).first()
                    current_post = Post.objects.create(user=user, content=content, community=_community)
                    positive_point = PositivePoint.objects.filter(user=user).first()
                    positive_point.point = positive_point.point + 1
                    positive_point.save()
                    serializer = PostSerializer(current_post)
                    return Response(serializer.data, status=200)
            return Response({Message.SC_BAD_RQ}, status=400)
        return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_BAD_RQ}, status=200)


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
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    post = Post.objects.filter(id=post_id).first()
    if post:
        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)
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
            post.up_vote.add(request.user)
            post.down_vote.remove(request.user)
            positive_point.point = positive_point.point + 2
            positive_point.save()
            return Response({Message.SC_OK}, status=200)
        if action == "down_vote":
            post.down_vote.add(request.user)
            post.up_vote.remove(request.user)
            positive_point.point = positive_point.point - 2
            positive_point.save()
            return Response({Message.SC_OK}, status=200)
        return Response({Message.SC_OK}, status=200)
    return Response({Message.SC_OK}, status=200)


@api_view(["GET"])
def user_post(request):
    if request.user.is_authenticated:
        query = Post.objects.filter(user=request.user)
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
    return Response({"Total: ": count_post_by_community(community_type)})


@api_view(["GET"])
def get_post_count(request):
    count = Post.objects.filter(user=request.user).count()
    return Response({"Total: ": count})


@api_view(["GET"])
def get_comment_count(request):
    count = Comment.objects.filter(user=request.user).count()
    return Response({"Total: ": count})


@api_view(["GET"])
def get_count_by_vote(request):
    up_vote_count = Post.objects.filter(up_vote=request.user).count()
    down_vote_count = Post.objects.filter(down_vote=request.user).count()
    return Response({"Total: ": up_vote_count + down_vote_count})


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


@api_view(["GET"])
def test(request):
    if request.user.is_authenticated:
        return Response({"hello"})
    return Response({"-hello"})
