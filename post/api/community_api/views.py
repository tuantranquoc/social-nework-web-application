from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from community.models import Community, SubCommunity
from post.models import Post, Comment, PositivePoint
from rest_framework.response import Response
from post.serializers import PostSerializer, CommentSerializer, CommunitySerializer

User = get_user_model()


# Community view api view

@api_view(['GET', 'POST'])
def community_create_view(request, name, *args, **kwargs):
    if request.user.is_authenticated:
        positive_point = PositivePoint.objects.filter(user=request.user).first()
        if positive_point.point <= 1:
            return Response({'detail': 'not enough positive point to create new community'}, status=400)
        if not SubCommunity.objects.filter(community_type=name) and SubCommunity.objects.create(community_type=name):
            return Response({}, status=200)
        return Response({'detail': 'community already exist!'}, status=400)
    else:
        return Response({}, 403)


@api_view(['GET', 'POST'])
def community_list_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        communities = Community.objects.all()
        serializer = CommunitySerializer(communities, many=True)
        return Response(serializer.data, status=200)
    else:
        return HttpResponse({}, 403)
