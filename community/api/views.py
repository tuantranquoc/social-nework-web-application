from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from community.models import Community
from post.serializers import CommunitySerializer
from redditv1.message import Message

User = get_user_model()


def get_paginated_queryset_response(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = CommunitySerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
def create_community(request):
    if request.user.is_authenticated:
        community = request.data.get("community")
        sub_community = request.data.get("sub_community")
        if not Community.objects.filter(community_type=community):
            return Response({Message.SC_NOT_FOUND}, status=400)
        if request.user.positivepoint.point <= 10:
            return Response({Message.SC_NOT_ENOUGH_POINT}, status=400)
        parent = Community.objects.filter(community_type=community).first()
        Community.objects.create(community_type=sub_community, parent=parent)
        return Response({Message.SC_OK}, status=201)


@api_view(["GET"])
def get_list_community_by_user(request):
    if request.user.is_authenticated:
        query = Community.objects.filter(user=request.user)
        return get_paginated_queryset_response(query, request)
    return Response({Message.SC_LOGIN_REDIRECT}, status=200)


@api_view(["POST"])
def community_action(request):
    if request.user.is_authenticated:
        community_type = request.data.get('community')
        action = request.data.get('action')
        community = Community.objects.filter(community_type=community_type).first()
        if community:
            if action == "follow":
                community.user.add(request.user)
            if action == "un_follow":
                community.user.remove(request.user)
            return Response({Message.SC_OK}, status=200)
        return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


@api_view(["GET"])
def get_list_community(request):
    query = Community.objects.all()
    return get_paginated_queryset_response(query, request)


@api_view(['GET'])
def change_state(request, community_type):
    if request.user.is_authenticated:
        if community_type:
            community = Community.objects.filter(creator=request.user, community_type=community_type).first()
            if community:
                community.state = not community.state
                community.save()
                return Response(Message.SC_OK, status=200)
            return Response(Message.SC_PERMISSION_DENIED, status=403)
        return Response(Message.SC_BAD_RQ, status=400)
    return Response(Message.SC_LOGIN_REDIRECT, status=403)
