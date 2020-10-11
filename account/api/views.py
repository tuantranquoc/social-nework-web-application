from django.contrib.auth import authenticate, login, get_user_model
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from account.models import Profile
from account.serializers import PublicProfileSerializer

User = get_user_model()


@api_view(["GET"])
def profile_list_view(request):
    profiles = Profile.objects.all()
    return get_paginated_queryset_recommend_user_response(profiles, request)


def get_paginated_queryset_recommend_user_response(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PublicProfileSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def profile_detail_view(request, username):
    profiles = Profile.objects.filter(user__username=username)
    return get_paginated_queryset_recommend_user_response(profiles, request)


# auth

@api_view(['GET', 'POST'])
def login_via_react_view(request, *args, **kwargs):
    username = request.data.get("username")
    password = request.data.get("password")
    print("login", username, password)
    user = authenticate(username=username, password=password)
    print("user", user)
    if user:
        login(request, user)
        return Response({}, status=200)
    return Response({}, status=404)


@api_view(['GET', 'POST'])
def register_via_react_view(request, *args, **kwargs):
    print("method", request.method)
    username = request.data.get("username")
    password = request.data.get("password")
    print("register-", username, password)
    if username and password:
        user = User.objects.create_user(username=username, password=password)
        if user:
            login(request, user)
        if not user:
            return Response({}, status=400)
    return Response({}, status=200)
