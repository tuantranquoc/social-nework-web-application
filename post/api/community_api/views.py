from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

from community.models import Community
from post.models import Post, Comment, PositivePoint
from rest_framework.response import Response
from post.serializers import PostSerializer, CommentSerializer, CommunitySerializer

User = get_user_model()


# Community view api view

# @api_view(['GET', 'POST'])
# def community_create_view(request, name, *args, **kwargs):
#     if request.user.is_authenticated:
#         positive_point = PositivePoint.objects.filter(user=request.user).first()
#         if positive_point.point <= 1:
#             return Response({'detail': 'not enough positive point to create new community'}, status=400)
#         if not SubCommunity.objects.filter(community_type=name) and SubCommunity.objects.create(community_type=name):
#             return Response({}, status=200)
#         return Response({'detail': 'community already exist!'}, status=400)
#     else:
#         return Response({}, 401)


@api_view(['GET', 'POST'])
def community_list_view(request, *args, **kwargs):
    communities = Community.objects.all()
    serializer = CommunitySerializer(communities, many=True)
    return Response(serializer.data, status=200)


def get_paginated_queryset_response(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = CommunitySerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)
