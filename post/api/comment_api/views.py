from django.http import HttpResponse
from rest_framework.decorators import api_view
from post.models import Post, Comment
from rest_framework.response import Response
from post.serializers import PostSerializer, CommentSerializer


# comment api view

@api_view(['GET'])
def comment_parent_list_view(request, comment_id, *args, **kwargs):
    if request.user.is_authenticated:
        comment = Comment.objects.filter(id=comment_id).first()
        comment = Comment.objects.filter(parent=comment)

        if not comment:
            return Response({}, status=204)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=200)


@api_view(['POST'])
def child_comment_create_view(request, comment_id, *args, **kwargs):
    """
    data = {"content":"CONTENT"}
    """
    if request.user.is_authenticated:
        comment = Comment.objects.filter(id=comment_id).first()

        if not comment:
            return Response({}, status=204)
        content = request.data.get("content")
        comment = Comment.objects.create(parent=comment, content=content, user=request.user)
        if comment:
            serializer = CommentSerializer(comment)
            return Response(serializer.data, status=201)
        return Response({"detail", "Bad Request"}, status=400)


@api_view(['POST'])  # http method client has send == POST
def comment_create_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        content = request.data.get("content")
        post_id = request.data.get("id")

        if content and post_id:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            comment = Comment.objects.filter(id=comment.id)
            serializer = CommentSerializer(comment, many=True)
            return Response(serializer.data, status=201)
    else:
        return Response({"detail": "Authentication credentials are not provided"}, status=403)


@api_view(['GET'])  # http method client has send == POST
def comment_api_view(request, post_id, *args, **kwargs):
    if request.user.is_authenticated:
        # Comment.objects.create(user_id=1, tweet=tweet, content="okay")
        # comment = Comment.objects.filter(tweet=tweet, user_id=1)
        comment = Comment.objects.filter(post_id=post_id)
        if not comment:
            return Response({}, status=204)
        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data, status=200)
    else:
        return HttpResponse(" not OKE1")
