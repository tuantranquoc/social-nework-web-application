from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from community.models import Community, SubCommunity
from post.models import Post
from rest_framework.response import Response
from post.serializers import PostSerializer


@api_view(["GET"])
def post_list_view(request):
    query = Post.objects.all()
    return get_paginated_queryset_response(query, request)


@api_view(["GET", "POST"])
def post_create_api(request):
    if not request.user.is_authenticated:
        return Response({"detail": "Redirect to login page"}, status=400)
    if request.method == "POST":
        content = request.data.get("content")
        community = request.data.get("community")
        sub_community = request.data.get("sub_community")
        if sub_community is None and community is None:
            return Response({"detail": "Community is require"}, status=400)
        user = request.user
        if content:
            if community and not Community.objects.filter(community_type=community).first():
                return Response({"detail": "Community not found"}, status=400)
            if sub_community and not SubCommunity.objects.filter(community_type=sub_community).first():
                return Response({"detail": "Community not found"}, status=400)
            _community = Community.objects.filter(community_type=community).first()
            _sub_community = SubCommunity.objects.filter(community_type=sub_community).first()
            current_post = Post.objects.create(user=user, content=content, community=_community or None,
                                               sub_community=_sub_community or None)
            serializer = PostSerializer(current_post)
            return Response(serializer.data, status=200)

        return Response({"detail": "content can not be null"}, status=201)
    return Response({"detail": "require method post for create 'post'"}, status=200)


@api_view(["POST"])
def post_delete_api(request, post_id):
    if not request.user.is_authenticated:
        return Response({"detail": "Redirect to login page"}, status=400)
    post = Post.objects.filter(id=post_id)
    if not post:
        return Response({"detail": "Post not found!"}, status=400)
    if not Post.objects.filter(user=request.user, id=post_id):
        return Response({"detail", "you dont have permission to process request!"}, status=401)

    post.delete()
    return Response("Delete post success!")


@api_view(["GET"])
def post_find_by_id(request, post_id):
    if not request.user.is_authenticated:
        return Response({"detail": "Redirect to login page"}, status=400)
    post = Post.objects.filter(id=post_id).first()
    if post:
        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)
    return Response({"detail": "post not found"}, status=204)


@api_view(["POST", "GET"])
def re_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({"detail": "Redirect to login page"}, status=401)
    post = Post.objects.filter(id=post_id).first()
    if post:
        new_post = Post.objects.create(parent=post, user=request.user)
        serializer = PostSerializer(new_post)
        return Response(serializer.data, status=200)
    return Response({"detail": "post not found"}, status=204)


@api_view(["POST"])
def post_action(request):
    if not request.user.is_authenticated:
        return Response({"detail": "Redirect to login page"}, status=401)
    post_id = request.data.get('id')
    action = request.data.get('action')
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({"detail": "post not found"}, status=204)
    if action:
        if action == "up_vote":
            post.up_vote.add(request.user)
            post.down_vote.remove(request.user)
            return Response({"detail": "Action up_vote success"}, status=200)
        if action == "down_vote":
            post.down_vote.add(request.user)
            post.up_vote.remove(request.user)
            return Response({"detail": "Action down_vote success"}, status=200)
        return Response({"detail": "Action success"}, status=200)
    return Response({"detail": "unknown action"}, status=200)


def get_paginated_queryset_response(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PostSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)
