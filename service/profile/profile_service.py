import base64
import operator
from functools import reduce

from django.contrib.auth import authenticate, login, get_user_model, logout
from django.core.files.base import ContentFile
from django.db.models import Q, Count
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from account.models import Profile, CustomColor
from account.serializers import PublicProfileSerializer
from post.models import Post
from post.serializers import PostSerializer
from redditv1.message import Message
from function.file import get_image, isValidHexaCode
from function.paginator import get_paginated_queryset_response
from redditv1.name import ModelName
from community.models import Community
from track.models import CommunityTrack, Track
from service.post.post_service import check_community_track
import datetime
User = get_user_model()


def profile_list_view(request):
    profiles = Profile.objects.all()
    page_size = request.data.get('page_size')
    return get_paginated_queryset_response(profiles, request, page_size,
                                           ModelName.PROFILE)


def profile_detail_view(request, username):
    page_size = request.data.get('page_size')
    profile = Profile.objects.filter(user__username=username).first()
    if profile:
        custom_color = CustomColor.objects.filter(profile=profile).first()
        if not custom_color:
            custom_color = CustomColor.objects.create()
            profile.custom_color = custom_color
            profile.save()
        if request.user.is_authenticated:
            track = Track.objects.filter(user=request.user).first()
            list_community = get_profile_top_community(profile.user)
            print('list', list_community)
            if list_community:
                for c in list_community:
                    check_community_track(track, c, request.user)
        profile = Profile.objects.filter(user__username=username)
    return get_paginated_queryset_response(profile, request, page_size,
                                           ModelName.PROFILE)


def profile_current_detail_view(request):
    page_size = request.data.get('page_size')
    if request.user.is_authenticated:
        profiles = Profile.objects.filter(user__username=request.user.username)
        return get_paginated_queryset_response(profiles, request, page_size,
                                               ModelName.PROFILE)
    return Response({}, status=400)
    # if not request.user.is_authenticated:
    #     profiles = Profile.objects.filter(user__username=request.user.username)
    #     return get_paginated_queryset_recommend_user_response(profiles, request)
    # return Response({}, status=400)


def profile_detail_api_view(request, username):
    # get the profile for the pass user name
    qs = Profile.objects.filter(user__username=username)
    if not qs.exists():
        return Response({"detail": "User not found"}, status=404)
    profile_obj = qs.first()
    serializer = PublicProfileSerializer(instance=profile_obj,
                                         context={"request": request})
    data = request.data or {}
    if request.method == "POST":
        me = request.user
        action = data.get("action")
        if profile_obj.user != me:
            if action == "follow":
                profile_obj.follower.add(me)
            elif action == "un_follow":
                profile_obj.follower.remove(me)
            else:
                pass
    return Response(serializer.data, status=200)


def profile_image_post(request):
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


def profile_avatar_post(request):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if request.data.get("img"):
            data = request.data.get("img")
            # profile.background = image
            profile.avatar = get_image(data)
            profile.save()
            return Response({}, status=200)
        else:
            return Response({}, status=400)
    else:
        return Response({}, status=401)


def profile_background_post(request):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        if request.data.get("img"):
            data = request.data.get("img")
            # profile.background = image
            profile.background = get_image(data)
            profile.save()
            return Response({}, status=200)
        else:
            return Response({}, status=400)
    else:
        return Response({}, status=401)


def profile_update_via_react_view(request):
    if not request.user.is_authenticated:
        return Response({}, status=401)
    user = request.user
    my_profile = user.profile
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    location = request.data.get("location")
    bio = request.data.get("bio")
    email = request.data.get("email")
    background = request.data.get("background")
    avatar = request.data.get("avatar")
    background_color = request.data.get("background_color")
    title_background_color = request.data.get("title_background_color")
    description_background_color = request.data.get(
        "description_background_color")
    button_background_color = request.data.get("button_background_color")
    button_text_color = request.data.get("button_text_color")
    text_color = request.data.get("text_color")
    post_background_color = request.data.get("post_background_color")
    custom_color = CustomColor.objects.filter(profile=my_profile).first()
    if not custom_color:
        custom_color = CustomColor.objects.create()
        my_profile.custom_color = custom_color
        my_profile.save()
    print(custom_color.background_color)
    if background_color:
        custom_color.background_color = background_color
    if background:
        if len(background) > len('data:,'):
            my_profile.background = get_image(background)
    if avatar:
        if len(avatar) > len('data:,'):
            my_profile.avatar = get_image(avatar)
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if email:
        user.email = email
    if background_color:
        if isValidHexaCode(background_color):
            my_profile.custom_color.background_color = background_color
        else:
            return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                            status=400)
    if description_background_color:
        if isValidHexaCode(description_background_color):
            my_profile.custom_color.description_background_color = description_background_color
        else:
            return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                            status=400)
    if title_background_color:
        if isValidHexaCode(title_background_color):
            my_profile.custom_color.title_background_color = title_background_color
        else:
            return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                            status=400)
    if button_background_color:
        if isValidHexaCode(button_background_color):
            my_profile.custom_color.button_background_color = button_background_color
        else:
            return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                            status=400)
    if button_text_color:
        if isValidHexaCode(button_text_color):
            my_profile.custom_color.button_text_color = button_text_color
        else:
            return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                            status=400)
    if text_color:
        if isValidHexaCode(text_color):
            my_profile.custom_color.text_color = text_color
        else:
            return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                            status=400)
    if post_background_color:
        if isValidHexaCode(post_background_color):
            my_profile.custom_color.post_background_color = post_background_color
        else:
            return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                            status=400)
    my_profile.location = location
    my_profile.bio = bio
    user.save()
    custom_color.save()
    my_profile.save()
    return Response({Message.DETAIL:Message.SC_OK}, status=200)


def get_following_profiles(request, username):
    page_size = request.data.get('page_size')
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user__username=username).first()
        if profile:
            following = profile.user.following.all()
            return get_paginated_queryset_response(following, request,
                                                   page_size,
                                                   ModelName.PROFILE)
        return Response({}, status=400)
    return Response({}, status=403)


def login_via_react_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        request.session["username"] = request.user.username
        return Response({Message.SC_OK}, status=200)
    return Response({Message.SC_NOT_FOUND}, status=404)


def register_via_react_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username and password:
        user = User.objects.create_user(username=username, password=password)
        if user:
            login(request, user)
        if not user:
            return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_OK}, status=200)


def logout_view_js(request):
    if request.method == 'POST':
        logout(request)
        return Response({}, status=200)
    if request.method == 'GET':
        logout(request)
        return Response({}, status=200)
    return Response({}, status=400)


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
                profile.follower.remove(request.user)
            return Response({Message.SC_OK}, status=200)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_NO_AUTH}, status=401)


def spilt_user_tag(hash_tag):
    if "@" in hash_tag:
        hash_tag_list = hash_tag.split("@")
        hash_tag_list.pop(0)
        return hash_tag_list
    return hash_tag


def search(request):
    page_size = request.data.get('page_size')
    key_word = request.data.get('key_word')
    search_type = request.data.get('search_type')
    if search_type == 'community':
        query = Community.objects.filter(community_type__icontains=key_word)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.COMMUNITY)
    if key_word:
        if '@' in key_word:
            tags = spilt_user_tag(key_word)
            print('ley_word', tags)
            profiles = Profile.objects.filter(
                reduce(operator.or_,
                       (Q(user__username__icontains=x) for x in tags)))
            return get_paginated_queryset_response(profiles, request,
                                                   page_size,
                                                   ModelName.PROFILE)
        if '#' in key_word:
            tags = spilt_content(key_word)
            query = Post.objects.filter(
                reduce(operator.or_, (Q(title__icontains=x) for x in tags)))
            if not query:
                query = Post.objects.filter(
                    reduce(operator.or_,
                           (Q(content__icontains=x) for x in tags)))
            return get_paginated_queryset_response(query, request, page_size,
                                                   ModelName.POST)

        query = Post.objects.filter(title__icontains=key_word)
        if not query:
            query = Post.objects.filter(content__icontains=key_word)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NOT_FOUND}, status=404)


def search_v0(request):
    page_size = request.data.get('page_size')
    key_word = request.data.get('key_word')
    search_type = request.data.get('search_type')
    if key_word:
        if search_type == 'community':
            query = Community.objects.filter(
                community_type__icontains=key_word)
            return get_paginated_queryset_response(query, request, page_size,
                                                   ModelName.COMMUNITY)
        if search_type == 'user':
            query = Profile.objects.filter(user__username__icontains=key_word)
            return get_paginated_queryset_response(query, request, page_size,
                                                   ModelName.PROFILE)
        query = Post.objects.filter(title__icontains=key_word)
        if not query:
            query = Post.objects.filter(content__icontains=key_word)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_BAD_RQ}, status=400)


def recommend_user_from_profile(request, username):
    """
    get list follower from this acc
    profile -> follower acc -> max follower count okay >?
    """
    page_size = request.data.get('page_size')
    if request.user.is_authenticated:
        user = request.user
        following = user.following.all()
        profile_user_following = User.objects.filter(username=username).first()
        profile_user_following = profile_user_following.following.all()
        user_profile = Profile.objects.filter(
            user__profile__in=profile_user_following)
        u = user_profile.annotate(count=Count('follower')).order_by("-count")
        u = u.exclude(user__profile__in=following).exclude(user=request.user)
        return get_paginated_queryset_response(u, request, page_size,
                                               ModelName.PROFILE)


def recommend_user_from_feed(request):
    """
    get all follower list from feed -> feed mean that all the tweet that user has follow
    get all the follower profile from em
    """
    page_size = request.data.get('page_size')
    if request.user.is_authenticated:
        user = request.user
        # profiles that this user follow
        profiles = user.following.all()
        _pr = Profile.objects.none()
        _pr1 = Profile.objects.none()
        # get their profiles to get following list
        pr = Profile.objects.filter(user__profile__in=profiles)
        for p in profiles:
            _pr = p.user.following.annotate(count=Count("follower")).exclude(
                user__profile__in=profiles).exclude(
                    user=request.user).order_by("-count")
            _pr1 = _pr1 | _pr
        profiles_ = set(_pr1)
        profile_list = Profile.objects.filter(
            user__profile__in=profiles_).annotate(
                count=Count("follower")).order_by("-count")
        return get_paginated_queryset_response(profile_list, request,
                                               page_size, ModelName.PROFILE)
    return Response({}, status=400)


def recommend_user_from_global(request):
    page_size = request.data.get('page_size')
    if request.user.is_authenticated:
        user = request.user
        following = user.following.all()
        profiles = Profile.objects.annotate(count=Count("follower")).exclude(
            user__profile__in=following).exclude(
                user=request.user).order_by("-count")
        return get_paginated_queryset_response(profiles, request, page_size,
                                               ModelName.PROFILE)
    return Response({}, status=400)


def spilt_content(hash_tag):
    if "#" in hash_tag:
        hash_tag_list = hash_tag.split("#")
        hash_tag_list.pop(0)
        return hash_tag_list
    return hash_tag


def get_profile_top_community(user):
    if user:
        community_list = Community.objects.filter(user=user).annotate(
            user_count=Count('user')).order_by("-user_count")[0:3]
        list_community_type = []
        for c in community_list:
            list_community_type.append(c.community_type)
        return list_community_type
    return []