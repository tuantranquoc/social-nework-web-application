from django.http import HttpResponse
from rest_framework.decorators import api_view
from post.models import Post, Comment, PositivePoint
from rest_framework.response import Response
from post.serializers import PostSerializer, CommentSerializer
from redditv1.message import Message


# comment api view

@api_view(['GET'])
def comment_parent_list_view(request, comment_id, *args, **kwargs):
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
        return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_NO_AUTH}, status=401)


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
        return Response({Message.SC_NO_AUTH}, status=403)


@api_view(['GET'])  # http method client has send == POST
def comment_api_view(request, post_id, *args, **kwargs):
    comment = Comment.objects.filter(post_id=post_id)
    # test comment count
    # test comment count
    if not comment:
        return Response({}, status=204)
    serializer = CommentSerializer(comment, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
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
            return Response(Message.SC_OK, status=200)
        if action == "down_vote":
            comment.up_vote.remove(request.user)
            comment.down_vote.add(request.user)
            return Response(Message.SC_OK, status=200)
        return Response(Message.SC_BAD_RQ, status=400)
    return Response(Message.SC_BAD_RQ, status=400)
