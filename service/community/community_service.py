import base64

from django.core.files.base import ContentFile
from django.db.models import Count, Q
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from account.models import Profile
from community.models import Community, CommunityBlackList, CommunityHistory, Member, MemberInfo, CommunityBlackListDetail, BlackListType
from post.models import PositivePoint
from post.serializers import CommunityGraphSerializer, CommunitySerializer
from redditv1.message import Message
from redditv1.name import Role
from django.utils import timezone
from function.file import get_image
from redditv1.name import ModelName, BLType
from function.paginator import get_paginated_queryset_response
from function.file import isValidHexaCode
import datetime
from service.post.post_service import timestamp_in_the_past_by_day
from functools import reduce
import operator

User = get_user_model()


def create_community(request):
    if request.user.is_authenticated:
        community = request.data.get("community")
        sub_community = request.data.get("sub_community")
        background = request.data.get("background")
        description = request.data.get("description")
        avatar = request.data.get("avatar")
        rule = request.data.get("rule")
        background_color = request.data.get("background_color")
        if request.user.positivepoint.point <= 10:
            return Response({Message.SC_NOT_ENOUGH_POINT}, status=400)
        if not sub_community:
            if Community.objects.filter(community_type=community):
                return Response({Message.SC_CM_EXIST}, status=200)
            if not request.user.is_staff:
                return Response({Message.SC_PERMISSION_DENIED}, status=403)
            community = Community.objects.create(community_type=community,
                                                 description=description,
                                                 rule=rule,
                                                 creator=request.user)
            if isValidHexaCode(background_color):
                community.background_color = background_color
            if background:
                if len(background) > len('data:,'):
                    community.background = get_image(background)
            if avatar:
                if len(avatar) > len('data:,'):
                    community.avatar = get_image(avatar)
            community.save()
            positive_point = PositivePoint.objects.filter(
                user=request.user).first()
            positive_point.point = positive_point.point - 10
            positive_point.save()
            serializer = CommunitySerializer(community,
                                             context={'request': request})
            return Response(serializer.data, status=201)
        if not Community.objects.filter(community_type=community):
            return Response({Message.SC_CM_NOT_FOUND}, status=204)

        community_exist = Community.objects.filter(
            community_type=sub_community).first()
        if community_exist:
            return Response({Message.SC_CM_EXIST}, status=200)
        parent = Community.objects.filter(community_type=community).first()
        community = Community.objects.create(community_type=sub_community,
                                             parent=parent,
                                             description=description,
                                             rule=rule,
                                             creator=request.user)
        if isValidHexaCode(background_color):
            community.background_color = background_color
        positive_point = PositivePoint.objects.filter(
            user=request.user).first()
        positive_point.point = positive_point.point - 10
        positive_point.save()
        if background:
            if len(background) > len('data:,'):
                community.background = get_image(background)
        if avatar:
            if len(avatar) > len('data:,'):
                community.avatar = get_image(avatar)
        community.save()
        serializer = CommunitySerializer(community,
                                         context={"request": request})
        return Response(serializer.data, status=201)


def get_community(request):
    page_size = request.data.get("page_size")
    community_type = request.data.get('community')
    print(community_type)
    if community_type:
        community = Community.objects.filter(
            community_type__icontains=community_type)
        return get_paginated_queryset_response(community, request, page_size,
                                               ModelName.COMMUNITY)
    return Response({Message.SC_NOT_FOUND}, status=204)


def get_list_community_by_user(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        query = Community.objects.filter(user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.COMMUNITY)
    return Response({Message.SC_LOGIN_REDIRECT}, status=200)


def community_action(request):
    if request.user.is_authenticated:
        community_type = request.data.get('community')
        action = request.data.get('action')
        community = Community.objects.filter(
            community_type=community_type).first()
        if community:
            member = Member.objects.filter(user=request.user).first()
            if not member:
                member = Member.objects.create(user=request.user)
            check_member(member, community, request.user, action)
            if action == "follow":
                community.user.add(request.user)
            if action == "un_follow":
                community.user.remove(request.user)
            return Response({Message.SC_OK}, status=200)
        return Response({Message.SC_NOT_FOUND}, status=204)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


def check_member(member, community, user, action):
    if community:
        if not member:
            print('member not ex')
            member = Member.objects.create(user=user)
            if action == 'follow':
                member_info = MemberInfo.objects.create(
                    community=community, timestamp=datetime.datetime.now())
                member_info.save()
                member.member_info.add(member_info)
                member.save()
            if action == 'un_follow':
                member.save()
        else:
            check_member_exist = Member.objects.filter(
                user=user, member_info__community=community).first()
            if not check_member_exist:
                print('member info not ex')
                member_info = MemberInfo.objects.create(
                    community=community, timestamp=datetime.datetime.now())
                if action == 'follow':
                    member_info.save()
                    member.member_info.add(member_info)
                    member.save()
            else:
                print('member info ex')
                member_info = MemberInfo.objects.filter(
                    member=check_member_exist, community=community).first()
                member_info.timestamp = datetime.datetime.now()
                if action == 'un_follow':
                    member_info.state = False
                if action == 'follow':
                    member_info.state = True
                member_info.save()
                member.save()


def get_list_community(request):
    page_size = request.data.get("page_size")
    query = Community.objects.all()
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.COMMUNITY)


def change_state(request, community_type):
    if request.user.is_authenticated:
        if community_type:
            community = Community.objects.filter(
                creator=request.user, community_type=community_type).first()
            if community:
                community.state = not community.state
                community.save()
                return Response(Message.SC_OK, status=200)
            return Response(Message.SC_PERMISSION_DENIED, status=403)
        return Response(Message.SC_BAD_RQ, status=400)
    return Response(Message.SC_LOGIN_REDIRECT, status=403)


def community_update(request):
    if not request.user.is_authenticated:
        return Response({}, status=401)
    user = request.user
    community_type = request.data.get('community_type')
    community = Community.objects.filter(
        creator=request.user, community_type=community_type).first()
    background = request.data.get("background")
    description = request.data.get("description")
    avatar = request.data.get("avatar")
    background_color = request.data.get("background_color")
    title_background_color = request.data.get("title_background_color")
    description_background_color = request.data.get(
        "description_background_color")
    button_background_color = request.data.get("button_background_color")
    button_text_color = request.data.get("button_text_color")
    text_color = request.data.get("text_color")
    post_background_color = request.data.get("post_background_color")

    if community:
        if background:
            if len(background) > len('data:,'):
                community.background = get_image(background)
        if avatar:
            if len(avatar) > len('data:,'):
                community.avatar = get_image(avatar)
        if description:
            community.description = description
        if background_color:
            if isValidHexaCode(background_color):
                community.background_color = background_color
            else:
                return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                                status=400)
        if description_background_color:
            if isValidHexaCode(description_background_color):
                community.description_background_color = description_background_color
            else:
                return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                                status=400)
        if title_background_color:
            if isValidHexaCode(title_background_color):
                community.title_background_color = title_background_color
            else:
                return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                                status=400)
        if button_background_color:
            if isValidHexaCode(button_background_color):
                community.button_background_color = button_background_color
            else:
                return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                                status=400)
        if button_text_color:
            if isValidHexaCode(button_text_color):
                community.button_text_color = button_text_color
            else:
                return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                                status=400)
        if text_color:
            if isValidHexaCode(text_color):
                community.text_color = text_color
            else:
                return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                                status=400)
        if post_background_color:
            if isValidHexaCode(post_background_color):
                community.post_background_color = post_background_color
            else:
                return Response({Message.DETAIL: Message.WRONG_INPUT_COLOR},
                                status=400)
        user.save()
        community.save()
        return Response({Message.DETAIL: Message.SC_OK}, status=200)
    return Response({Message.DETAIL: Message.SC_CM_NOT_FOUND}, status=400)


def recommend_sub_community(request, community):
    page_size = request.data.get("page_size")
    sub_community = Community.objects.filter(parent__community_type=community)
    if request.user.is_authenticated:
        sub_community = Community.objects.filter(
            parent__community_type=community).exclude(user=request.user)
    return get_paginated_queryset_response(sub_community, request, page_size,
                                           ModelName.COMMUNITY)


def recommend_community(request):
    page_size = request.data.get("page_size")
    community = Community.objects.all().annotate(
        user_count=Count('user')).order_by('user_count')
    if request.user.is_authenticated:
        community = Community.objects.all().exclude(
            user=request.user).annotate(
                user_count=Count('user')).order_by('user_count')
    return get_paginated_queryset_response(community, request, page_size,
                                           ModelName.COMMUNITY)


def community_graph(request):
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    page_size = request.data.get('page_size')
    print('detect')
    if from_timestamp:
        print("timestamp: ", from_timestamp)
    if from_timestamp is not None and to_timestamp is not None:
        query = Community.objects.filter(
            timestamp__gte=from_timestamp,
            timestamp__lte=to_timestamp,
        )
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.COMMUNITY_GRAPH)
    query = Community.objects.filter(
        timestamp__gte=timestamp_in_the_past_by_day(30),
        timestamp__lte=timezone.now(),
    )
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.COMMUNITY_GRAPH)


def mod_action(request):
    community = request.data.get('community')
    user_id = request.data.get('user_id')
    action = request.data.get('action')
    if not action:
        return Response({Message.DETAIL: Message.SC_BAD_RQ}, status=400)
    if request.user.is_authenticated:
        user = User.objects.filter(id=user_id).first()
        community = Community.objects.filter(community_type=community).first()
        if not community or not user:
            return Response({Message.DETAIL: Message.SC_NOT_FOUND}, status=204)
        community_check = community.creator == request.user
        if not community_check:
            return Response({Message.DETAIL: Message.SC_PERMISSION_DENIED},
                            status=403)
        history = CommunityHistory.objects.filter(user=request.user,
                                                  community=community,
                                                  target=user).first()
        if not history:
            history = CommunityHistory.objects.create(user=request.user,
                                                      community=community,
                                                      target=user)
        member = Member.objects.filter(user=user).first()
        if member:
            member_info = MemberInfo.objects.filter(
                member=member, community=community).first()
            if member_info:
                current_member = MemberInfo.objects.filter(
                    member=member, community=community).first()
                print('has member info, old role: ', current_member.role)
                print('action:', action)
                if action == 'add':
                    print('current role', current_member.role, Role.MOD)
                    if current_member.role == Role.MEMBER:
                        history.old_role = current_member.role
                        history.new_role = Role.MOD
                        current_member.role = history.new_role
                        print('new_role', history.new_role)
                        community.mod.add(user)
                        history.timestamp = timezone.now()
                        history.save()
                        community.save()
                elif action == 'remove':
                    if current_member.role == Role.MOD:
                        print('demote')
                        history.old_role = current_member.role
                        history.new_role = Role.MEMBER
                        current_member.role = history.new_role
                        community.mod.remove(user)
                        history.timestamp = timezone.now()
                        community.save()
                        history.save()
                current_member.save()
            history.timestamp = timezone.now()
            print(current_member.role, history.new_role, 'after update')
            return Response({Message.DETAIL: Message.SC_OK}, status=200)
        return Response({Message.DETAIL: Message.USER_MUST_BE_MEMBER},
                        status=403)
    return Response({Message.DETAIL: Message.SC_NO_AUTH}, status=401)


def member_list(request):
    """
        data = "community":"community"
    """
    page_size = request.data.get('page_size')
    community = request.data.get('community')
    if community:
        community = Community.objects.filter(community_type=community).first()
        if community:
            member_info = MemberInfo.objects.filter(community=community)
            member = Member.objects.filter(member_info__in=member_info)
            profile = Profile.objects.filter(
                reduce(operator.or_, (Q(user=x.user) for x in member)))
            return get_paginated_queryset_response(profile, request, page_size,
                                                   ModelName.PROFILE)
    return Response({Message.DETAIL: Message.SC_BAD_RQ}, 400)


def add_use_to_community_blacklist(request):
    user_id = request.data.get('user_id')
    community = request.data.get('community')
    type = request.data.get('type')
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    '''
        mod and mod can not add another mod or admin into blacklist
        default in black list is 1 day
    '''
    if request.user.is_authenticated:
        if user_id and community and type:
            changed_by = request.user
            target_profile = Profile.objects.filter(user__id=user_id).first()
            community = Community.objects.filter(
                community_type=community).first()
            if target_profile and community:
                if target_profile.user == community.creator:
                    return Response(
                        {Message.DETAIL: Message.SC_PERMISSION_DENIED},
                        status=403)
 
                member = Member.objects.filter(user=request.user).first()
                if request.user == community.creator:
                    if not member:
                        member = Member.objects.create(user=request.user)
                        member_info = MemberInfo.objects.create(community=community, role=Role.ADMIN)
                        member.member_info.add(member_info)
                        member.save()
                member_info = MemberInfo.objects.filter(
                    member=member, community=community).first()
                target_member = Member.objects.filter(
                    user=target_profile.user).first()
                target_member_info = MemberInfo.objects.filter(
                    member=target_member, community=community).first()
                print('change by',member_info.role, 'target',target_member_info.role)
                if member_info and target_member_info:
                    if member_info.role == Role.ADMIN or target_member_info.role == Role.MOD:
                        blacklist = CommunityBlackList.objects.filter(
                            community=community).first()
                        if not blacklist:
                            blacklist = CommunityBlackList.objects.create(
                                community=community)
                        blacklist_detail = CommunityBlackListDetail.objects.filter(
                            user=target_profile.user,
                            communityblacklist=blacklist).first()
                        if not blacklist_detail:
                            blacklist_detail = CommunityBlackListDetail.objects.create(communityblacklist=blacklist)
                            blacklist_detail.user.add(target_profile.user)
                        default_blacklist_type()
                        blacklist_type = BlackListType.objects.filter(
                            type=type).first()
                        blacklist.blacklist_detail = blacklist_detail
                        blacklist.save()
                        blacklist_detail.user.add(target_profile.user)
                        blacklist_detail.blacklist_type = blacklist_type
                        if not from_timestamp or not to_timestamp:
                            blacklist_detail.from_timestamp = timezone.now()
                            blacklist_detail.to_timestamp = timestamp_in_the_past_by_day(
                                1)
                        else:
                            blacklist_detail.from_timestamp = from_timestamp
                            blacklist_detail.to_timestamp = to_timestamp
                        blacklist_detail.save()
                        return Response({Message.DETAIL:Message.SC_OK}, status=200)
                return Response({Message.DETAIL: Message.SC_NOT_FOUND},
                                status=204)
            return Response({Message.DETAIL: Message.SC_CM_NOT_FOUND},
                            status=204)
        return Response({Message.DETAIL: Message.SC_BAD_RQ},
                            status=400)
    return Response({Message.DETAIL: Message.SC_NO_AUTH},
                            status=401)


def default_blacklist_type():
    blacklist_type = BlackListType.objects.all()
    if blacklist_type.count() == 0:
        type_1 = BlackListType.objects.create(
            type=BLType.VIEW_ONLY,
            description=
            'User can not search, see post, post on target community')
        type_1.save()
        type_2 = BlackListType.objects.create(
            type=BLType.BLOCK,
            description='User can not post in target community')
        type_2.save()


def timestamp_in_the_past_by_day(days):
    return timezone.now() - datetime.timedelta(days)