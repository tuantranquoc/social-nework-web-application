import base64

from django.contrib.auth import authenticate, login, get_user_model
from django.core.files.base import ContentFile
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


@api_view(['GET', 'POST'])
def profile_detail_api_view(request, username, *args, **kwargs):
    # get the profile for the pass user name
    print("user: ", request.user)
    print("target:", username)
    qs = Profile.objects.filter(user__username=username)
    print(qs)
    if not qs.exists():
        return Response({"detail": "User not found"}, status=404)
    profile_obj = qs.first()
    serializer = PublicProfileSerializer(instance=profile_obj, context={"request": request})
    data = request.data or {}
    print(data)
    if request.method == "POST":
        me = request.user
        action = data.get("action")
        if profile_obj.user != me:
            if action == "follow":
                profile_obj.follower.add(me)
            elif action == "unfollow":
                profile_obj.follower.remove(me)
            else:
                pass
    return Response(serializer.data, status=200)


@api_view(['GET', 'POST'])
def profile_image_post(request, *args, **kwargs):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user)
        if request.FILES:
            image = request.FILES['img']
            profile = profile.first()
            print(type(image))
            # profile.background = image
            print("past background", profile.background)
            profile.background = image
            profile.save()
            print("current", profile.background)
            return Response({}, status=200)
        else:
            return Response({}, status=400)
    else:
        return Response({}, status=401)


@api_view(['GET', 'POST'])
def profile_avatar_post(request, *args, **kwargs):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if request.data.get("img"):
            data = request.data.get("img")
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            # profile.background = image
            print("past background", profile.avatar)
            profile.avatar = image
            profile.save()
            print("current", profile.avatar)
            return Response({}, status=200)
        else:
            return Response({}, status=400)
    else:
        return Response({}, status=401)


@api_view(['GET', 'POST'])
def profile_background_post(request, *args, **kwargs):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if request.data.get("img"):
            data = request.data.get("img")
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            # profile.background = image
            print("past background", profile.background)
            profile.background = image
            profile.save()
            print("current", profile.background)
            return Response({}, status=200)
        else:
            return Response({}, status=400)
    else:
        return Response({}, status=401)


@api_view(['GET'])
def get_following_profiles(request, username, *args, **kwargs):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user__username=username).first()
        print(profile)
        if profile:
            following = profile.user.following.all()
            return get_paginated_queryset_recommend_user_response(following, request)
        return Response({}, status=400)
    return Response({}, status=403)


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
