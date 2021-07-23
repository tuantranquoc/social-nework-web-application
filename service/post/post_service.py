from community.models import Community, Member, MemberInfo
from django.db.models.aggregates import Count
from function.paginator import get_paginated_queryset_response
from post.models import Comment, PositivePoint, Post, PostType, View, UserVote
from account.models import Profile
from redditv1.name import ModelName
from rest_framework.response import Response
from redditv1.message import Message
from redditv1.name import CommentState, Role
from function.file import get_image
from post import rank
from post.serializers import PostSerializer
from django.utils import timezone
import datetime
from track.models import CommunityTrack, Track
from functools import reduce
import operator
from django.db.models import Q
import datetime
from notify.models import EntityType, Notification, NotificationChange, NotificationObject, UserNotify, CommunityNotify
from django.contrib.auth import get_user_model
import random
from operator import itemgetter
import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
from datetime import timedelta
# from track.models import CommunityTrack, Track

User = get_user_model()


def count_post_by_community(community):
    count = 0
    if Post.objects.filter(community__community_type=community):
        count = Post.objects.filter(
            community__community_type=community).count()
    return count


def timestamp_in_the_past_by_day(days):
    return timezone.now() - datetime.timedelta(days)


def parent_comment(comment_list, level):
    comments = []
    if level == 3:
        for level_3 in comment_list:
            comments.append(level_3.parent.parent)
    if level == 2:
        for level_2 in comment_list:
            comments.append(level_2.parent)
    return comments


def get_post_list(request, sort):
    # sort = request.data.get("sort")
    page_size = request.data.get("page_size")
    # this algorithm
    print("sort", sort)
    if sort == 'hot' or not sort:
        if request.user.is_authenticated:
            # print("comming in hot")
            # track = Track.objects.filter(user=request.user).first()
            # if not track:
            #     track = Track.objects.create(user=request.user)
            #     track.save()
            # community_track = CommunityTrack.objects.filter(
            #     track=track).order_by('-timestamp')[0:4]
            # list_community_track = []
            # for c in community_track:
            #     list_community_track.append(c.community.community_type)
            # community = Community.objects.filter(
            #     community_type__in=list_community_track)
            # query = Post.objects.filter(
            #     community__community_type__in=list_community_track).order_by(
            #         '-point')
            # if query.count() == 0:
            #     print("zero query")
            #     member = Community.objects.all()
            #     array = []
            #     for x in Community.objects.all():
            #         print("community", Member.objects.filter(member_info__community=x))
            #         array.append({"count": Member.objects.filter(member_info__community=x).count(),"id": x.id})
            #         # member_info_list = Member.objects.annotate(count=Count("member_info", filter=Q(member_info__community=x))).order_by("count").distinct
            #     print("array", array)
            #     top_community = sorted(array, key=lambda x: x['count'], reverse=True)

            #     print("top community", top_community)
            #     community_list = Community.objects.filter(id__in=[x["id"] for x in top_community])
            #     post_list = Post.objects.filter(community__in=Community.objects.filter(id__in=[x["id"] for x in top_community])).order_by("-point")

            #     return get_paginated_queryset_response(post_list, request, page_size,
            #                                         ModelName.POST)
            # return get_paginated_queryset_response(query, request, page_size,
            #                                        ModelName.POST)
            member = Community.objects.filter(user=request.user)
            array = []
            if member.count() == 0:
                for x in Community.objects.all():
                    array.append({"count": Member.objects.filter(
                        member_info__community=x).count(), "id": x.id})
                # member_info_list = Member.objects.annotate(count=Count("member_info", filter=Q(member_info__community=x))).order_by("count").distinct

                top_community = sorted(array, key=lambda k: k['count'])[10:]
                community_list = Community.objects.filter(
                    id__in=[x["id"] for x in top_community])
                post_list = Post.objects.filter(community__in=Community.objects.filter(
                    id__in=[x["id"] for x in top_community])).exclude(viewed=request.user).order_by("-point")
                # print(post.count())
                return get_paginated_queryset_response(post_list, request, page_size,
                                                       ModelName.POST)
            for x in member:
                print("community", Member.objects.filter(
                    member_info__community=x))
                array.append({"count": Member.objects.filter(
                    member_info__community=x).count(), "id": x.id})
                # member_info_list = Member.objects.annotate(count=Count("member_info", filter=Q(member_info__community=x))).order_by("count").distinct
            print("array", array)
            top_community = sorted(
                array, key=lambda x: x['count'], reverse=True)

            print("top community", top_community)
            community_list = Community.objects.filter(
                id__in=[x["id"] for x in top_community])
            post_list = Post.objects.filter(community__in=Community.objects.filter(
                id__in=[x["id"] for x in top_community])).exclude(viewed=request.user).order_by("-point")

            return get_paginated_queryset_response(post_list, request, page_size,
                                                   ModelName.POST)

        else:
            member = Community.objects.all()
            array = []
            for x in Community.objects.all():
                print(Member.objects.filter(
                    member_info__community=x).count())
                array.append({"count": Member.objects.filter(
                    member_info__community=x).count(), "id": x.id})
                # member_info_list = Member.objects.annotate(count=Count("member_info", filter=Q(member_info__community=x))).order_by("count").distinct

            top_community = sorted(array, key=lambda k: k['count'])
            print(top_community)
            community_list = Community.objects.filter(
                id__in=[x["id"] for x in top_community])
            post_list = Post.objects.filter(community__in=Community.objects.filter(
                id__in=[x["id"] for x in top_community])).order_by("-point")
            # print(post.count())
            return get_paginated_queryset_response(post_list, request, page_size,
                                                   ModelName.POST)

    if sort == 'best':
        if request.user.is_authenticated:
            rating_list_p2 = []
            user_list_p2 = []
            item_list_p2 = []
            recommend_list = []
            post_list = Post.objects.all()
            # for post in post_list:
            #     vote_list = post.vote.all()
            #     for v in vote_list:
            #         rating_list_p2.append(v.get_rating())
            #         user_list_p2.append(v.user.id)
            #         item_list_p2.append(post.id)
            uv_list = UserVote.objects.all()
            for uv in uv_list:
                rating_list_p2.append(uv.get_rating())
                user_list_p2.append(uv.user.id)
                item_list_p2.append(uv.post.id)
            if len(item_list_p2) == len(user_list_p2) == len(rating_list_p2):
                print("we got what we want lol!")
            rating_dict = {
                "user": user_list_p2,
                "item": item_list_p2,
                "rating": rating_list_p2
            }
            df = pd.DataFrame(rating_dict)
            reader = Reader(rating_scale=(1, 5))
            # Loads Pandas dataframe
            data = Dataset.load_from_df(df[["user", "item", "rating"]], reader)
            sim_options = {
                "name": "cosine",
                "user_based": True,  # Compute  similarities between items
            }
            algo = KNNWithMeans(sim_options=sim_options)
            trainingSet = data.build_full_trainset()
            algo.fit(trainingSet)
            prediction = algo.predict(17, 149)[4]["was_impossible"]
            print(prediction)
            post_list = Post.objects.filter(
                id__in=[x.post.id for x in uv_list]).exclude(viewed=request.user)
            for p in post_list:
                rt_dict = {}
                rt_dict["id"] = p.id
                predict = algo.predict(request.user.id, p.id)
                if predict[4]["was_impossible"] == True:
                    continue
                rt_dict["point"] = predict.est
                recommend_list.append(rt_dict)
            # for p in uv_list:
            #     rt_dict = {}
            #     rt_dict["id"] = uv.post.id
            #     rt_dict["point"] = algo.predict(request.user.id, uv.post.id).est
            #     recommend_list.append(rt_dict)
            recommend_list.sort(
                key=lambda item: item.get("point"), reverse=True)
            print(recommend_list[0:10])
            post_id_list = []
            post_list = []
            post_list_1 = []
            for r in recommend_list:
                post_list_1.append(Post.objects.filter(pk=r["id"]).first())
            return get_paginated_queryset_response(post_list_1, request, page_size,
                                                   ModelName.POST)
    top_community = Community.objects.filter(state=True).annotate(
        user_count=Count('user')).order_by('-user_count')

    if sort == 'new':
        if request.user.is_authenticated:
            # track = Track.objects.filter(user=request.user).first()
            # if not track:
            #     track = Track.objects.create(user=request.user)
            #     track.save()
            # community_track = CommunityTrack.objects.filter(
            #     track=track).order_by('-timestamp')[0:4]
            # list_community_track = []
            # for c in community_track:
            #     list_community_track.append(c.community.community_type)
            # community = Community.objects.filter(
            #     community_type__in=list_community_track)
            # query = Post.objects.filter(
            #     community__community_type__in=list_community_track).order_by(
            #         '-timestamp')
            # if query.count() == 0:
            #     print("zero query")
            #     member = Community.objects.all()
            #     array = []
            #     for x in Community.objects.all():
            #         print("community", Member.objects.filter(member_info__community=x))
            #         array.append({"count": Member.objects.filter(member_info__community=x).count(),"id": x.id})
            #         # member_info_list = Member.objects.annotate(count=Count("member_info", filter=Q(member_info__community=x))).order_by("count").distinct
            #     print("array", array)
            #     top_community = sorted(array, key=lambda x: x['count'], reverse=True)

            #     print("top community", top_community)
            #     community_list = Community.objects.filter(id__in=[x["id"] for x in top_community])
            #     post_list = Post.objects.filter(community__in=Community.objects.filter(id__in=[x["id"] for x in top_community])).order_by("-timestamp","-point")

            #     return get_paginated_queryset_response(post_list, request, page_size,
            #                                         ModelName.POST)
            # return get_paginated_queryset_response(query, request, page_size,
            #                                        ModelName.POST)
            member = Community.objects.filter(user=request.user)
            array = []
            for x in Community.objects.all():
                print("community", Member.objects.filter(
                    member_info__community=x))
                array.append({"count": Member.objects.filter(
                    member_info__community=x).count(), "id": x.id})
                # member_info_list = Member.objects.annotate(count=Count("member_info", filter=Q(member_info__community=x))).order_by("count").distinct
            print("array", array)
            top_community = sorted(
                array, key=lambda x: x['count'], reverse=True)

            print("top community", top_community)
            community_list = Community.objects.filter(
                id__in=[x["id"] for x in top_community])
            post_list = Post.objects.filter(community__in=Community.objects.filter(
                id__in=[x["id"] for x in top_community])).exclude(viewed=request.user).order_by("-timestamp")
            # post_list = Post.objects.all().order_by("-timestamp")
            return get_paginated_queryset_response(post_list, request, page_size,
                                                   ModelName.POST)

        else:
            member = Community.objects.all()
            array = []
            for x in Community.objects.all():
                array.append({"count": Member.objects.filter(
                    member_info__community=x).count(), "id": x.id})
                # member_info_list = Member.objects.annotate(count=Count("member_info", filter=Q(member_info__community=x))).order_by("count").distinct

            top_community = sorted(array, key=lambda k: k['count'])[10:]
            community_list = Community.objects.filter(
                id__in=[x["id"] for x in top_community])
            post_list = Post.objects.filter(community__in=Community.objects.filter(
                id__in=[x["id"] for x in top_community])).order_by("-timestamp")
            # print(post.count())
            return get_paginated_queryset_response(post_list, request, page_size,
                                                   ModelName.POST)
    if sort == "top":
        # post_list = Post.objects.annotate(num_vote=Count("up_vote",  filter=Q(created_at__gt=(datetime.datetime.now(), timedelta.days(1)))))
        option = request.data.get("option")
        print("opt", option)
        # if option != "day" or option != "month" or option != "week":
        #     return Response({"Missing option"}, status=400)
        day = 1
        if option == "day":
            day = 1
        elif option == "week":
            day = 7
        elif option == "month":
            day = 30
        else:
            return Response({"Missing option"}, status=400)
        if request.user.isAuthenticated:
            post_list = Post.objects.filter(timestamp__gte=(datetime.datetime.now() -  timedelta(days=day))).exclude(viewed=request.user).annotate(num_vote=Count("up_vote")).order_by("-num_vote")
        else:
            post_list = Post.objects.filter(timestamp__gte=(datetime.datetime.now() -  timedelta(days=day))).annotate(num_vote=Count("up_vote")).order_by("-num_vote")

        return get_paginated_queryset_response(post_list, request, page_size, ModelName.POST)
                                            #    timestamp__range=(datetime.datetime.now(), timedelta.days(1))

    return Response({Message.SC_BAD_RQ}, status=400)


def handle_notification(post):
    entity_type = EntityType.objects.filter(id=6).first()
    community = post.community
    notification_object = NotificationObject.objects.create(
        entity_type=entity_type, post=post)
    notifycation_change = NotificationChange.objects.create(
        user=post.user, notification_object=notification_object)
    notification = Notification.objects.filter(community=community).first()
    print("in handle notifications")
    if notification:
        print("in handle notifications 1")
        user_notify_list = notification.user_notify.all()
        for n in user_notify_list:
            print("in for")
            print(n.user.username)
            print(n.status)
            if n.status == False:
                split_message = "has created post in community " + community.community_type
                n.notification_object.add(notification_object)
                message = ""
                parent = n.parent
                while parent is not None:
                    p = UserNotify.objects.filter(pk=parent.id).first()
                    parent = p.parent
                n_object_list = n.notification_object.order_by("-created_at")
                for n_b in n_object_list:
                    message += (n_b.post.user.username + " ")
                message = message.split()
                message = list(dict.fromkeys(message))
                notify_message = ""
                connect_message = " "
                if len(message) > 3:
                    connect_message += "and " + (len(message) - 3) + " others "
                for i in range(len(message)):
                    if i > 2:
                        break
                    notify_message += (message[i] + " ")
                print("message", notify_message + " " + split_message)
                print("notify_id", n.id)
                notify_message = notify_message + connect_message + split_message
                n.message = notify_message
                n.save()

            if n.status == True:
                new_notify = UserNotify.objects.create(user=n.user, parent=n)
                notification.user_notify.remove(n)
                notification.user_notify.add(new_notify)
                notification.save()
                new_notify.notification_object.add(notification_object)
                n_object_list = new_notify.notification_object.order_by(
                    "-created_at")
                message = ""
                for n_b in n_object_list:
                    message += (n_b.post.user.username + " ")
                message = message.split()
                message = list(dict.fromkeys(message))
                print(len(message))
                notify_message = ""
                for i in range(len(message)):
                    if i > 2:
                        break
                    notify_message += (message[i] + " ")
                print("message-status = 1",
                      notify_message + " " + split_message)
                notify_message = notify_message + " " + split_message
                new_notify.message = notify_message
                new_notify.save()
                print("create new notify message")
    else:
        print("in here")
        print("in handle notifications 2")
        notification = Notification.objects.create(community=community)
        member_info = MemberInfo.objects.filter(community=community)
        member = Member.objects.filter(member_info__in=member_info)
        if member:
            for x in member:
                print(x.user.username)
            profiles = Profile.objects.filter(
                reduce(operator.or_, (Q(user=x.user) for x in member)))
            print("profile count",profiles.count)
            for p in profiles:
                print("profile", p)
                user_notify = UserNotify.objects.create(user=p.user)
                user_notify.notification_object.add(notification_object)
                split_message = post.user.username + " has created post in community " + community.community_type
                user_notify.message = split_message
                user_notify.save()
                notification.user_notify.add(user_notify)
            notification.save()


def create_post(request):
    """
    data = {"title":"","content":"","community":"","type":"","image":"optional"}
    ---
    request_serializer: PostSerializer
    response_serializer: PostSerializer
    """
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    if request.method == "POST":
        title = request.data.get("title")
        content = request.data.get("content")
        community = request.data.get("community")
        image = request.data.get('image')
        type = request.data.get('type')
        if community is None:
            return Response({Message.SC_BAD_RQ}, status=400)
        user = request.user
        if community:
            if Community.objects.filter(community_type=community):
                _community = Community.objects.filter(
                    community_type=community).first()
                positive_point = PositivePoint.objects.filter(
                    user=user).first()
                positive_point.point = positive_point.point + 1
                positive_point.save()
                if image:
                    if len(image) > len('data:,'):
                        current_post = Post.objects.create(
                            user=user,
                            content=content,
                            community=_community,
                            title=title,
                            type=PostType.objects.filter(type=type).first())
                        current_post.image = get_image(image)
                        current_post.point = rank.hot(0, 0,
                                                      current_post.timestamp)
                        current_post.save()
                        serializer = PostSerializer(
                            current_post, context={"request": request})
                        return Response(serializer.data, status=201)
                current_post = Post.objects.create(
                    user=user,
                    content=content,
                    community=_community,
                    title=title,
                    type=PostType.objects.filter(type=type).first())
                current_post.point = rank.hot(0, 0, current_post.timestamp)
                current_post.save()
                print("new post created")
                if current_post:
                    handle_notification(current_post)
                    # entity_type = EntityType.objects.filter(id=1).first()
                    # notification_object = NotificationObject.objects.create(entity_type=entity_type, post=current_post)
                    # notifycation_change = NotificationChange.objects.create(user=request.user, notification_object=notification_object)
                    # notification = Notification.objects.create(notification_object=notification_object)
                    # member_info = MemberInfo.objects.filter(community=_community)
                    # member = Member.objects.filter(member_info__in=member_info)
                    # profiles = Profile.objects.filter(
                    #     reduce(operator.or_, (Q(user=x.user) for x in member)))
                    # for p in profiles:
                    #     user_notify = UserNotify.objects.create(user=p.user)
                    #     notification.user_notify.add(user_notify)
                    # notification.save()
                    ############################################
                    # notification_object = NotificationObject.objects.create(
                    #     entity_type=entity_type, post=current_post)
                    # notifycation_change = NotificationChange.objects.create(
                    #     user=request.user,
                    #     notification_object=notification_object)
                    # notification = Notification.objects.filter(
                    #     community=_community).first()
                    # if notification:
                    #     print("hello world")
                    # else:
                    #     notification = Notification.objects.create(
                    #         community=_community)
                    #     member_info = MemberInfo.objects.filter(
                    #         community=_community)
                    #     member = Member.objects.filter(
                    #         member_info__in=member_info)
                    #     profiles = Profile.objects.filter(
                    #         reduce(operator.or_,
                    #                (Q(user=x.user) for x in member)))
                    #     for p in profiles:
                    #         user_notify = UserNotify.objects.create(
                    #             user=p.user)
                    #         user_notify.notification_object.add(
                    #             notification_object)
                    #         user_notify.save()
                    #         notification.user_notify.add(user_notify)
                    #     notification.save()
                serializer = PostSerializer(current_post,
                                            context={"request": request})
                return Response(serializer.data, status=201)
        return Response({Message.SC_BAD_RQ}, status=400)
    return Response({Message.SC_BAD_RQ}, status=400)


def find_post_by_id(request, post_id):
    post = Post.objects.filter(id=post_id).first()
    if post:
        if post.community.state is True:
            if not request.user.is_authenticated:
                serializer = PostSerializer(post, context={"request": request})
                return Response(serializer.data, status=200)
            if post.user == request.user:
                track = Track.objects.filter(user=request.user).first()
                check_community_track(track, post.community, request.user)
                serializer = PostSerializer(post, context={"request": request})
                return Response(serializer.data, status=200)
            if request.user.is_authenticated:
                user_vote = UserVote.objects.filter(
                    user=request.user, post=post).first()
                if not user_vote:
                    UserVote.objects.create(
                        user=request.user, post=post, view=1)
                else:
                    user_vote.view = 1
            track = Track.objects.filter(user=request.user).first()
            check_community_track(track, post.community, request.user)
            view = View.objects.filter(user=request.user, post=post).first()
            serializer = check_view(view, post, request.user, request)
            post.viewed.add(request.user)
            return Response(serializer.data, status=200)
        if post.community.state is False:
            if not request.user.is_authenticated:
                return Response({Message.SC_LOGIN_REDIRECT}, status=401)
            view = View.objects.filter(user=request.user, post=post).first()
            if Community.objects.filter(user=request.user,
                                        community_type=post.community):
                serializer = check_view(view, post, request.user, request)
                return Response(serializer.data, status=200)
            return Response({Message.MUST_FOLLOW}, status=400)
    return Response({Message.SC_NOT_FOUND}, status=204)


def check_view(view, post, user, request):
    if not view:
        view = View.objects.create(post=post)
        view.user.add(user)
        view.save()
    if view.old_timestamp is None:
        view.old_timestamp = timezone.now()
        view.save()
        post.view_count = post.view_count + 1
        post.save()
        serializer = PostSerializer(post, context={"request": request})
        return serializer
    if view.old_timestamp is not None:
        difference = (timezone.now() - view.old_timestamp).total_seconds()
        if difference >= 120:
            post.view_count = post.view_count + 1
            view.old_timestamp = timezone.now()
            view.save()
            post.save()
        serializer = PostSerializer(post, context={"request": request})
        return serializer


def check_community_track(track, community, user):
    community = Community.objects.filter(community_type=community).first()
    if community:
        if not track:
            track = Track.objects.create(user=user)
            community_track = CommunityTrack.objects.create(
                community=community, timestamp=datetime.datetime.now())
            community_track.save()
            track.community_track.add(community_track)
            track.save()
        else:
            check_tracking_exist = Track.objects.filter(
                user=user, community_track__community=community).first()
            if not check_tracking_exist:
                community_track = CommunityTrack.objects.create(
                    community=community, timestamp=datetime.datetime.now())
                community_track.save()
                track.community_track.add(community_track)
                track.save()
            else:
                community_track = CommunityTrack.objects.filter(
                    track=check_tracking_exist, community=community).first()
                community_track.timestamp = datetime.datetime.now()
                community_track.save()
                track.save()


def check_track(track, user):
    if not track:
        track = Track.objects.create(user=user)
        track.save()


def re_post(request, post_id):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    post = Post.objects.filter(id=post_id).first()
    if post:
        new_post = Post.objects.create(parent=post, user=request.user)
        serializer = PostSerializer(new_post, context={"request": request})
        return Response(serializer.data, status=200)
    return Response({Message.SC_NOT_FOUND}, status=204)


def action(request):
    if not request.user.is_authenticated:
        return Response({Message.SC_LOGIN_REDIRECT}, status=401)
    post_id = request.data.get('id')
    action = request.data.get('action')
    post = Post.objects.filter(id=post_id).first()
    if not post:
        return Response({Message.SC_NOT_FOUND}, status=204)
    if action:
        positive_point = PositivePoint.objects.filter(
            user=request.user).first()
        if not positive_point:
            positive_point = PositivePoint.objects.create(user=request.user)
        if action == "up_vote":
            if Post.objects.filter(id=post_id, up_vote=request.user):
                post.up_vote.remove(request.user)
                positive_point.point = positive_point.point - 2
                positive_point.save()
                post.point = rank.hot(post.up_vote.count(),
                                      post.down_vote.count(), post.timestamp)
                post.save()
                track = Track.objects.filter(user=request.user).first()
                check_community_track(track, post.community, request.user)
                number_of_up_vote = post.up_vote.count()
                number_of_down_vote = post.down_vote.count()
                return Response({
                    "current_vote": "",
                    "number_of_up_vote": number_of_up_vote,
                    "number_of_down_vote": number_of_down_vote
                }, status=200)
            user_vote = UserVote.objects.filter(
                user=request.user, post=post).first()
            if not user_vote:
                UserVote.objects.create(
                    user=request.user, post=post, view=1, like=1)
            else:
                user_vote.view = 1
                user_vote.like = 1
                user_vote.down_vote = 0
                user_vote.save()
            post.up_vote.add(request.user)
            post.down_vote.remove(request.user)
            positive_point.point = positive_point.point + 2
            positive_point.save()
            post.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                  post.timestamp)
            post.save()
            track = Track.objects.filter(user=request.user).first()
            check_community_track(track, post.community, request.user)
            number_of_up_vote = post.up_vote.count()
            number_of_down_vote = post.down_vote.count()
            return Response({
                "current_vote": "up_vote",
                "number_of_up_vote": number_of_up_vote,
                "number_of_down_vote": number_of_down_vote
            }, status=200)
        if action == "down_vote":
            if Post.objects.filter(id=post_id, down_vote=request.user):
                post.down_vote.remove(request.user)
                positive_point.point = positive_point.point + 2
                positive_point.save()
                post.point = rank.hot(post.up_vote.count(),
                                      post.down_vote.count(), post.timestamp)
                post.save()
                number_of_up_vote = post.up_vote.count()
                number_of_down_vote = post.down_vote.count()
                return Response({
                    "current_vote": "",
                    "number_of_up_vote": number_of_up_vote,
                    "number_of_down_vote": number_of_down_vote
                }, status=200)
            user_vote = UserVote.objects.filter(
                user=request.user, post=post).first()

            if not user_vote:
                UserVote.objects.create(
                    user=request.user, post=post, view=1, like=1)
            else:
                user_vote.view = 1
                user_vote.down_vote = 1
                user_vote.like = 0
                user_vote.save()

            post.down_vote.add(request.user)
            post.up_vote.remove(request.user)
            positive_point.point = positive_point.point - 2
            positive_point.save()
            post.point = rank.hot(post.up_vote.count(), post.down_vote.count(),
                                  post.timestamp)
            post.save()
            number_of_up_vote = post.up_vote.count()
            number_of_down_vote = post.down_vote.count()
            return Response({
                "current_vote": "down_vote",
                "number_of_up_vote": number_of_up_vote,
                "number_of_down_vote": number_of_down_vote
            }, status=200)
        if action == "favorite":
            if post in request.user.profile.favorite.all():
                # return Response({Message.SC_OK}, status=200)
                request.user.profile.favorite.remove(post)
                user_vote = UserVote.objects.filter(user=request.user, post=post).first()
                if not user_vote:
                    UserVote.objects.create(
                        user=request.user, post=post, view=1, share=0)
                else:
                    user_vote.share = 0
                    user_vote.save()
                return Response({Message.SC_OK}, status=200)
            else:
                request.user.profile.favorite.add(post)
                user_vote = UserVote.objects.filter(user=request.user, post=post).first()
                if not user_vote:
                    UserVote.objects.create(
                        user=request.user, post=post, view=1, share=1)
                else:
                    user_vote.share = 1
                    user_vote.save()
                return Response({Message.SC_CREATED}, status=201)
    return Response({Message.SC_BAD_RQ}, status=400)


def find_post_by_user(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        query = Post.objects.filter(user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)


def find_post_by_up_vote(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        query = Post.objects.filter(user=request.user).annotate(
            user_count=Count("up_vote")).order_by("-user_count").filter(
                community__user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)


def find_post_by_community(request, community_type):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(
        community__community_type=community_type, hidden_in_community=False, hidden=False)
    community = Community.objects.filter(community_type=community_type).first()
    if not community:
        return Response({Message.SC_NOT_FOUND}, status=204)
    if request.user.is_authenticated:
        if community.state == True:
            return get_paginated_queryset_response(post, request, page_size,
                                                   ModelName.POST)
        post = post.filter(user=request.user)
        if post:
            return get_paginated_queryset_response(post, request, page_size,
                                                   ModelName.POST)
        return Response({Message.MUST_FOLLOW}, status=403)
    if community.state == False:
        return Response({Message.MUST_FOLLOW}, status=403)
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def find_post_by_comment(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        # level 1
        comment_list = Comment.objects.filter(user=request.user,
                                              parent__isnull=True)
        # level 2 + 3
        comment_list_level_3 = Comment.objects.filter(
            parent__isnull=False).filter(parent__parent__isnull=False).filter(
                parent__parent__parent__isnull=True, user=request.user)
        comment_list_level_2 = Comment.objects.filter(
            parent__isnull=False).filter(parent__parent__isnull=True,
                                         user=request.user)
        query = Post.objects.filter(comment__in=comment_list)
        query_2 = Post.objects.filter(
            comment__in=parent_comment(comment_list_level_2, 2))
        query_3 = Post.objects.filter(
            comment__in=parent_comment(comment_list_level_3, 3))
        query_result = (query | query_2 | query_3).distinct()
        return get_paginated_queryset_response(query_result, request,
                                               page_size, ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)


def find_post_by_comment_with_username(request, username):
    page_size = request.data.get("page_size")
    # level 1
    comment_list = Comment.objects.filter(user__username=username,
                                          parent__isnull=True)
    # level 2 + 3
    comment_list_level_3 = Comment.objects.filter(parent__isnull=False).filter(
        parent__parent__isnull=False).filter(
            parent__parent__parent__isnull=True, user__username=username)
    comment_list_level_2 = Comment.objects.filter(parent__isnull=False).filter(
        parent__parent__isnull=True, user__username=username)
    query = Post.objects.filter(comment__in=comment_list)
    query_2 = Post.objects.filter(
        comment__in=parent_comment(comment_list_level_2, 2))
    query_3 = Post.objects.filter(
        comment__in=parent_comment(comment_list_level_3, 3))
    query_result = (query | query_2 | query_3).distinct()
    return get_paginated_queryset_response(query_result, request, page_size,
                                           ModelName.POST)


def find_post_by_down_vote(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        post = Post.objects.filter(down_vote=request.user)
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


# def find_post_by_comment(request):


def find_post_by_username_down_vote(request, username):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        no_block = Post.objects.filter(down_vote__username=username,
                                       community__user=request.user)

        return get_paginated_queryset_response(no_block, request,
                                               page_size, ModelName.POST)
    post = Post.objects.filter(down_vote__username=username,
                               community__state=True)
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def find_post_by_username_up_vote(request, username):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        no_block = Post.objects.filter(up_vote__username=username,
                                       community__user=request.user)
        if no_block:
            return get_paginated_queryset_response(no_block, request,
                                                   page_size, ModelName.POST)
        return Response({Message.SC_NOT_FOUND}, status=400)
    post = Post.objects.filter(up_vote__username=username,
                               community__state=True)
    if post:
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NOT_FOUND}, status=400)


def trending(request):
    page_size = request.data.get("page_size")
    days = request.data.get("days")
    if days:
        past = timestamp_in_the_past_by_day(days)
        post = Post.objects.filter(
            community__state=True,
            timestamp__gte=past,
            timestamp__lte=datetime.datetime.now()).annotate(
                user_count=Count("up_vote")).order_by('-user_count')
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    post = Post.objects.filter(community__state=True).annotate(
        user_count=Count("up_vote")).order_by('-user_count')
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def hot(request):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(
        community__state=True,
        timestamp__gte=timestamp_in_the_past_by_day(1),
        timestamp__lte=datetime.datetime.now()).order_by('-point')
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def find_post_by_up_vote(request):
    page_size = request.data.get("page_size")
    if request.user.is_authenticated:
        post = Post.objects.filter(up_vote=request.user)
        if post:
            return get_paginated_queryset_response(post, request, page_size,
                                                   ModelName.POST)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_LOGIN_REDIRECT}, status=401)


def recent(request):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(community__state=True).order_by('-timestamp')
    return get_paginated_queryset_response(post, request, page_size,
                                           ModelName.POST)


def get_post_by_time_interval(request):
    from_timestamp = request.data.get('from_timestamp')
    to_timestamp = request.data.get('to_timestamp')
    page_size = request.data.get('page_size')
    type = request.data.get('type')
    model = ModelName.POST
    if type == 'graph':
        model = ModelName.POST_GRAPH
    if request.user.is_authenticated:
        if from_timestamp is not None and from_timestamp != '' and to_timestamp != '' and to_timestamp is not None:
            from_timestamp = datetime.datetime.fromtimestamp(
                int(from_timestamp))
            to_timestamp = datetime.datetime.fromtimestamp(int(to_timestamp))

            top_community = Community.objects.filter(user=request.user).union(
                Community.objects.filter(community__state=True)).union(
                    Community.objects.filter(creator=request.user)).distinct()
            query = Post.objects.filter(
                user=request.user,
                timestamp__gte=from_timestamp,
                timestamp__lte=to_timestamp).union(
                    Post.objects.filter(
                        community__user=request.user,
                        timestamp__gte=from_timestamp,
                        timestamp__lte=to_timestamp)).union(
                            Post.objects.filter(
                                user__following=Profile.objects.filter(
                                    user=request.user).first(),
                                timestamp__gte=from_timestamp,
                                timestamp__lte=to_timestamp)).union(
                                    Post.objects.filter(
                                        community__state=True,
                                        timestamp__gte=from_timestamp,
                                        timestamp__lte=to_timestamp).distinct(
                                    )).distinct().order_by('-point')
            # query = Post.objects.filter(timestamp__gte=from_timestamp,
            #                             timestamp__lte=to_timestamp,
            #                             user=request.user)

            return get_paginated_queryset_response(query, request, page_size,
                                                   model)
        if (from_timestamp is None or to_timestamp is None
                or from_timestamp != ''
                or to_timestamp != '') and (from_timestamp is not None
                                            or to_timestamp is not None):
            return Response({Message.DETAIL: Message.SC_BAD_RQ}, status=400)
        query = Post.objects.filter(
            timestamp__gte=timestamp_in_the_past_by_day(30),
            timestamp__lte=timezone.now(),
            user=request.user)
        return get_paginated_queryset_response(query, request, page_size,
                                               model)
    return Response({Message.DETAIL: Message.SC_NO_AUTH}, status=401)


def delete_post(request):
    id = request.data.get('id')
    check_community()
    if request.user:
        if request.user.is_authenticated:
            post = Post.objects.filter(id=id).first()
            if post:
                if post.user == request.user:
                    post.state = CommentState.DELETED
                    post.save()
                    return Response({Message.DETAIL: Message.SC_OK},
                                    status=200)
                if post.community:
                    member = Member.objects.filter(user=request.user).first()
                    if member:
                        member_info = MemberInfo.objects.filter(
                            member=member, community=post.community).first()
                        if member_info.role == Role.MOD:
                            post.state = CommentState.HIDDEN
                            post.save()
                            return Response({Message.DETAIL: Message.SC_OK},
                                            status=200)
                    if post.community.creator == request.user:
                        post.state = CommentState.HIDDEN
                        post.save()
                        return Response({Message.DETAIL: Message.SC_OK},
                                        status=200)
                return Response({Message.DETAIL: Message.SC_PERMISSION_DENIED},
                                status=403)
            return Response({Message.DETAIL: Message.SC_NOT_FOUND}, status=204)
        return Response({Message.DETAIL: Message.SC_NO_AUTH}, status=401)
    return Response({Message.DETAIL: Message.SC_BAD_RQ}, status=400)


def check_community():
    community = Community.objects.all()
    for c in community:
        if not c.creator:
            c.creator = Profile.objects.filter().first().user
            c.save()
            
            



def get_rating_list(request):
    if not request.user.is_authenticated:
        return Response({Message.DETAIL: Message.SC_NO_AUTH}, status=401)
