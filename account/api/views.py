import base64
import operator
from functools import reduce

from django.contrib.auth import authenticate, login, get_user_model, logout
from django.core.files.base import ContentFile
from django.db.models import Q, Count
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from account.models import Profile
from account.serializers import PublicProfileSerializer
from post.models import Post
from post.serializers import PostSerializer
from redditv1.message import Message

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


@api_view(["GET"])
def profile_current_detail_view(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.filter(user__username=request.user.username)
        return get_paginated_queryset_recommend_user_response(profiles, request)
    return Response({}, status=400)
    # if not request.user.is_authenticated:
    #     profiles = Profile.objects.filter(user__username=request.user.username)
    #     return get_paginated_queryset_recommend_user_response(profiles, request)
    # return Response({}, status=400)


@api_view(['GET', 'POST'])
def profile_detail_api_view(request, username, *args, **kwargs):
    # get the profile for the pass user name

    qs = Profile.objects.filter(user__username=username)

    if not qs.exists():
        return Response({"detail": "User not found"}, status=404)
    profile_obj = qs.first()
    serializer = PublicProfileSerializer(instance=profile_obj, context={"request": request})
    data = request.data or {}

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

            # profile.background = image

            profile.background = image
            profile.save()

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

            profile.avatar = image
            profile.save()

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

            profile.background = image
            profile.save()

            return Response({}, status=200)
        else:
            return Response({}, status=400)
    else:
        return Response({}, status=401)


@api_view(['POST'])
def profile_update_via_react_view(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return Response({}, status=401)
    user = request.user
    my_profile = user.profile
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    location = request.data.get("location")
    bio = request.data.get("bio")
    email = request.data.get("email")
    if request.data.get("background"):
        data = request.data.get("background")
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        my_profile.background = image
    if request.data.get("avatar"):
        data = request.data.get("avatar")
        format, imgstr = data.split(';base64,')
        ext = format.split('/')[-1]
        image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        my_profile.avatar = image
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    my_profile.location = location
    my_profile.bio = bio
    user.save()
    my_profile.save()
    if not my_profile.background or not my_profile.avatar:
        return Response({Message.SC_BAD_IMG}, status=400)
    return Response({}, status=200)


@api_view(['GET'])
def get_following_profiles(request, username, *args, **kwargs):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user__username=username).first()
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
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        request.session["username"] = request.user.username

        return Response({Message.SC_OK}, status=200)
    return Response({Message.SC_NOT_FOUND}, status=404)


@api_view(['GET', 'POST'])
def register_via_react_view(request, *args, **kwargs):
    username = request.data.get("username")
    password = request.data.get("password")
    if username and password:
        user = User.objects.create_user(username=username, password=password)
        if user:
            login(request, user)
        if not user:
            return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_OK}, status=200)


@api_view(['GET', 'POST'])
def logout_view_js(request, *args, **kwargs):
    if request.method == 'POST':
        logout(request)
        return Response({}, status=200)
    if request.method == 'GET':
        logout(request)
        return Response({}, status=200)
    return Response({}, status=400)


@api_view(['GET', 'POST'])
def register_via_react_view(request, *args, **kwargs):
    username = request.data.get("username")
    password = request.data.get("password")
    if username and password:
        user = User.objects.create_user(username=username, password=password)
        if not user:
            return Response({}, status=400)
    return Response({}, status=200)


@api_view(['POST'])
def profile_action(request):
    if request.user.is_authenticated:
        user_id = request.data.get("id")
        action = request.data.get("action")
        profile = Profile.objects.filter(user__id=user_id).first()
        if profile:
            if action == "follow":
                profile.follower.add(request.user)
                return Response({Message.SC_OK}, status=200)
            if action == "un_follow":
                profile.follower.add(request.user)
            return Response({Message.SC_OK}, status=200)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_NO_AUTH}, status=401)


def spilt_user_tag(hash_tag):
    if "@" in hash_tag:
        hash_tag_list = hash_tag.split("@")
        hash_tag_list.pop(0)
        return hash_tag_list
    return hash_tag


@api_view(['POST'])
def search(request):
    key_word = request.data.get('key_word')
    if key_word:
        if '@' in key_word:
            tags = spilt_user_tag(key_word)
            profiles = Profile.objects.filter(user__username__in=tags)
            return get_paginated_queryset_recommend_user_response(profiles, request)
        if '#' in key_word:
            tags = spilt_content(key_word)
            query = Post.objects.filter(reduce(operator.and_, (Q(content__contains=x) for x in tags)))
            return get_paginated_queryset_response(query, request, 10)
        query = Post.objects.filter(content__contains=key_word)
        return get_paginated_queryset_response(query, request, 10)


@api_view(['GET'])
def recommend_user_from_profile(request, username, *args, **kwargs):
    """
    get list follower from this acc
    profile -> follower acc -> max follower count okay >?
    """
    if request.user.is_authenticated:
        user = request.user
        following = user.following.all()
        print(following)
        profile_user_following = User.objects.filter(username=username).first()
        profile_user_following = profile_user_following.following.all()
        print(profile_user_following)
        user_profile = Profile.objects.filter(user__profile__in=profile_user_following)
        u = user_profile.annotate(count=Count('follower')).order_by(
            "-count"
        )
        u = u.exclude(user__profile__in=following).exclude(user=request.user)
        return get_paginated_queryset_recommend_user_response(u, request)


@api_view(['GET'])
def recommend_user_from_feed(request, *args, **kwargs):
    """
    get all follower list from feed -> feed mean that all the tweet that user has follow
    get all the follower profile from em
    """
    if request.user.is_authenticated:
        user = request.user
        # profiles that this user follow
        profiles = user.following.all()

        _pr = Profile.objects.none()
        _pr1 = Profile.objects.none()

        # get their profiles to get following list
        pr = Profile.objects.filter(user__profile__in=profiles)

        for p in profiles:
            _pr = p.user.following.annotate(count=Count("follower")).exclude(user__profile__in=profiles).exclude(
                user=request.user).order_by("-count")

            _pr1 = _pr1 | _pr

        idss = set(_pr1)

        profile_list = Profile.objects.filter(user__profile__in=idss).annotate(count=Count("follower")).order_by(
            "-count")
        print(profile_list)
        return get_paginated_queryset_recommend_user_response(profile_list, request)
    return Response({}, status=400)


@api_view(['GET'])
def recommend_user_from_global(request, *args, **kwargs):
    if request.user.is_authenticated:
        user = request.user
        following = user.following.all()
        print("following user", following)
        profiles = Profile.objects.annotate(count=Count("follower")).exclude(user__profile__in=following).exclude(
            user=request.user).order_by("-count")

        print(profiles)
        return get_paginated_queryset_recommend_user_response(profiles, request)
    return Response({}, status=400)


def spilt_content(hash_tag):
    if "#" in hash_tag:
        hash_tag_list = hash_tag.split("#")
        hash_tag_list.pop(0)
        return hash_tag_list
    return hash_tag


def get_paginated_queryset_response(query_set, request, page_size):
    paginator = PageNumberPagination()
    paginator.page_size = page_size
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PostSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)
