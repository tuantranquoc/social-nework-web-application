import base64
import datetime
from django.core.files.base import ContentFile
from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from account.models import Profile
from community.models import Community
from post import rank
from post.models import Comment, PositivePoint, Post, PostType, UserVote, View
from rest_framework.response import Response
from post.serializers import PostSerializer, PostTypeSerializer, PostGraphSerializer
from django.contrib.auth import get_user_model
from function.paginator import get_paginated_queryset_response
from function.file import get_image

from redditv1.message import Message
from redditv1.name import ModelName
from service.post import post_service
import random
from scipy import spatial
from service.post import post_service
User = get_user_model()


@api_view(["GET", "POST"])
def post_list_view(request):
    """
    ``GET`` or ``POST``  Return lists all post where being sort as ``BEST`` or ``HOT`` from current ``User``

    **Example request**:
    .. code-block:: json

        {
            "sort":"best",
            "page_size":"5"
        }
    """

    return post_service.get_post_list(request)


@api_view(["POST"])
def post_create_api(request):
    """
    **Example request**:
    .. code-block:: json

        {
            "title": "new title",
            "content": "hello world",
            "community": "anime",
            "type":"content",
            "image":"base64"
        }


    **Example response**:
    .. code-block:: json
    
        {
            "user": {
                "first_name": "tran quoc",
                "last_name": "tuan",
                "id": 1,
                "location": null,
                "bio": null,
                "color": {
                    "id": 1,
                    "background_color": "#30363A",
                    "title_background_color": "#30363C",
                    "description_background_color": "#30363C",
                    "button_background_color": "#30363C",
                    "button_text_color": "#30363C",
                    "text_color": "#30363C",
                    "post_background_color": "#30363C"
                },
                "follower_count": 1,
                "following_count": 2,
                "is_following": false,
                "username": "tuantran",
                "background": "http://127.0.0.1:8000/media/evagelion.jpg",
                "avatar": "http://127.0.0.1:8000/media/user.png",
                "timestamp": "2020-09-14T16:22:53.013134Z",
                "email": "17521226@gm.uit.edu.vn"
            },
            "id": 144,
            "title": "new title",
            "content": "helloworld",
            "parent": null,
            "timestamp": "2021-04-18T08:58:37.243823Z",
            "image": null,
            "up_vote": 0,
            "down_vote": 0,
            "community_type": "anime",
            "type": "content",
            "view_count": 0,
            "point": "10771.30",
            "state": "public"
        }
    """
    return post_service.create_post(request)


@api_view(["POST"])
def post_delete_api(request):
    """
    ``POST`` delete ``Post`` by ``Post_id``
    **Example response**:
    .. code-block:: json

    {
        "id":"1"
    }
    """
    return post_service.delete_post(request)


@api_view(["GET"])
def find_post_by_id(request, post_id):
    """
    ``GET`` find ``Post`` by ``Post_id``
    """
    return post_service.find_post_by_id(request, post_id)


@api_view(["POST", "GET"])
def re_post(request, post_id):
    """
    ``RE_POST`` posted_post by current user
    """
    return post_service.re_post(request, post_id)


@api_view(["POST"])
def post_action(request):
    """
    ``UP_VOTE or DOWN_VOTE POST``
    
    There is two options action: ``up_vote`` and ``down_vote``

    **Example request**:
    .. code-block:: json

        {
            "id": "1",
            "action": "up_vote"
        }
    """
    return post_service.action(request)


@api_view(["GET", "POST"])
def get_list_post_by_user(request):
    """
    ``GET`` Return list posted by current user.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    return post_service.find_post_by_user(request)


@api_view(["GET"])
def get_list_post_by_up_vote(request):
    """
    ``GET`` Return list voted by current user
    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def user_comment_post(request):
    """
    ``GET`` Return list commented by current user

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    if request.user.is_authenticated:
        comment = Comment.objects.filter(user=request.user)
        # return get_paginated_queryset_response(query, request)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_community(request, community_type):
    """
    ``GET`` Return total number of post in provied community
    """
    return Response({"Total": count_post_by_community(community_type)})


@api_view(["GET"])
def get_post_count(request):
    """
    ``GET`` Return total number of post posted by current user
    """
    if request.user.is_authenticated:
        count = Post.objects.filter(user=request.user).count()
        return Response({"Total": count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_comment_count(request):
    """
    ``GET`` Return total number of comment by current user
    """
    if request.user.is_authenticated:
        count = Comment.objects.filter(user=request.user).count()
        return Response({"Total": count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_vote(request):
    """
    ``GET`` Return total number of voted by current user
    """
    if request.user.is_authenticated:
        up_vote_count = Post.objects.filter(up_vote=request.user).count()
        down_vote_count = Post.objects.filter(down_vote=request.user).count()
        return Response({"Total": up_vote_count + down_vote_count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_up_vote(request):
    """
    ``GET`` Return total number of up_voted by current user
    """
    if request.user.is_authenticated:
        up_vote_count = Post.objects.filter(up_vote=request.user).count()
        return Response({"Total": up_vote_count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_username_up_vote(request, username):
    """
    ``GET`` Return total number of up_voted by provide user
    """
    if request.user.is_authenticated:
        up_vote_count = Post.objects.filter(up_vote__username=username).count()
        return Response({"Total": up_vote_count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_down_vote(request):
    """
    ``GET`` Return total number of down_voted by current user
    """
    if request.user.is_authenticated:
        down_vote_count = Post.objects.filter(down_vote=request.user).count()
        return Response({"Total": down_vote_count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_username_down_vote(request, username):
    """
    ``GET`` Return total number of down_voted by current user
    """
    if request.user.is_authenticated:
        down_vote_count = Post.objects.filter(
            down_vote__username=username).count()
        return Response({"Total": down_vote_count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_user_vote(request, username):
    """
    ``GET`` Return total number of voted by current user
    """
    if request.user.is_authenticated:
        up_vote_count = Post.objects.filter(up_vote__username=username).count()
        down_vote_count = Post.objects.filter(
            down_vote__username=username).count()
        return Response({"Total": up_vote_count + down_vote_count})
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["POST"])
def check_vote(request):
    """
    ``POST`` Check if user has up_vote or down_vote post provide

    **Example request**:
    .. code-block:: json

        {
            "id": "5"
        }
    """
    if not request.user.is_authenticated:
        return Response({Message.SC_NO_AUTH}, status=401)
    post_id = request.data.get('id')
    if post_id:
        post = Post.objects.filter(id=post_id)
        if not post:
            return Response({Message.SC_NOT_FOUND}, status=400)
        if Post.objects.filter(up_vote=request.user, id=post_id):
            return Response({"up_vote"})
        if Post.objects.filter(down_vote=request.user, id=post_id):
            return Response({"down_vote"})
        return Response({Message.USER_HAS_NOT_VOTE_POST}, status=200)
    return Response({Message.SC_BAD_RQ}, status=400)


@api_view(["GET", "POST"])
def filter_by_up_vote(request):
    """
    ``GET POST`` Return list of post has up_voted by current user

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    if request.user.is_authenticated:
        page_size = request.data.get("page_size")
        query = Post.objects.annotate(
            user_count=Count("up_vote")).order_by("-user_count").filter(
                community__state=True)
        return get_paginated_queryset_response(query, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET", "POST"])
def get_post_by_comment(request):
    """
    ``GET`` Return list of post has commented by current user
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    if request.user.is_authenticated:
        return post_service.find_post_by_comment(request)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET", "POST"])
def get_post_by_username_comment(request, username):
    """
    ``GET, POST`` Return list of post has commented by provided user
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    return post_service.find_post_by_comment_with_username(
            request, username)


@api_view(["GET", "POST"])
def find_post_by_user(request, username):
    """
    ``GET`` Return list of posted post by provied user
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """

    page_size = request.data.get("page_size")
    post = Post.objects.filter(user__username=username, community__state=True)
    if post:
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET", "POST"])
def count_post_by_user(request, username):
    """
    ``GET, POST`` Return total number of posted post by provied user
    """
    if request.user.is_authenticated:
        count = Post.objects.filter(user__username=username).count()
        if count:
            return Response({"Total": count}, status=200)
        return Response({Message.SC_NOT_FOUND}, status=400)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def find_post_by_up_vote(request):
    """
    ``GET`` Return list of up_voted post of current user
    """
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def find_post_by_username_up_vote(request, username):
    """
    ``GET`` Return list of up_voted post by provied user
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    return post_service.find_post_by_username_up_vote(request, username)


@api_view(["GET"])
def find_post_by_down_vote(request):
    """
    ``GET`` Return list of down_voted post of current user
    """
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def find_post_by_username_down_vote(request, username):
    """
    ``GET`` Return list of down_voted post by provied user
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5"
        }
    """
    return post_service.find_post_by_username_down_vote(request, username)


@api_view(['GET', 'POST'])
def trending(request):
    """
    ``GET`` Return list of trending post by time interval provided
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5",
            "days": "30"
        }
    """
    return post_service.trending(request)


@api_view(['GET', 'POST'])
def hot(request):
    """
    ``GET`` Return list of hot post by time interval provided
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5",
        }
    """
    return post_service.hot(request)


@api_view(['GET', 'POST'])
def recent(request):
    """
    ``GET`` Return list of recent post by time interval provided
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5",
        }
    """
    return post_service.recent(request)


@api_view(['GET'])
def get_type_list(request):
    """
    ``GET`` Return list of post type
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "page_size": "5",
        }
    """
    page_size = request.data.get("page_size")
    query = PostType.objects.all()
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.POST_TYPE)


@api_view(["POST", "GET"])
def get_post_by_time_interval(request):
    """
    ``GET`` Return list of post by time interval
    Default page_size is 5.

    **Example request**:
    .. code-block:: json

        {
            "from_timestamp":"from_timestamp",
            "to_timestamp":"to_timestamp",
            "page_size":"page_size",
            "type":"type"
        }
    """
    return post_service.get_post_by_time_interval(request)


@api_view(["GET"])
def reset(request):
    # query = PostPoint.objects.all()
    # query.delete()
    post = Post.objects.all()
    for p in post:
        # post_point = PostPoint.objects.filter(post=p)
        # if not post_point:
        #     PostPoint.objects.create(post=p,
        #                              point=rank.hot(p.up_vote.count(), p.down_vote.count(), datetime.datetime.now()))
        p.point = rank.hot(p.up_vote.count(), p.down_vote.count(), p.timestamp)
        p.save()
    return Response({Message.SC_OK}, status=200)


@api_view(["GET", "POST"])
def find_post_by_community(request, community_type):
    return post_service.find_post_by_community(request, community_type)


def count_post_by_community(community):
    count = 0
    if Post.objects.filter(community__community_type=community):
        count = Post.objects.filter(
            community__community_type=community).count()
    return count


"""
    create random rating dataset
"""
# @api_view(["GET"])
# def create_ratting_dataset(request):
#     if not request.user.is_authenticated:
#         return Response({Message.DETAIL: Message.SC_NO_AUTH}, status=401)
#     user_list = User.objects.all()
#     post_list = Post.objects.all()
#     for post in post_list:
#         for user in user_list:
#             report = random.randint(0,1)
#             dislike = random.randint(0,1)
#             view = random.randint(0,1)
#             like = random.randint(0,1)
#             share = random.randint(0,1)
#             rate = UserVote.objects.create(user=user, report=report, dislike=dislike, view=view, like=like, share=share)
#             post.vote.add(rate)
#             post.save()


@api_view(["GET"])
def get_rating_dict(request):
    if not request.user.is_authenticated:
        return Response({Message.DETAIL: Message.SC_NO_AUTH}, status=401)
    rating_dict = {"user": [], "item": [], "rating": []}
    post_list = Post.objects.all()
    for post in post_list:
        # rating_dict[1].add(post.id)
        items = rating_dict["item"]
        rating_dict.update(user=items.append(post.id))
        users = rating_dict["user"]
        rating_dict.update(user=items.append(post.id))
    print(rating_dict["item"])


from operator import itemgetter
import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
from track.models import CommunityTrack, Track


def sum_average_list(a):
    average = sum(a) / len(a)
    for i in range(len(a)):
        a[i] = a[i] - average
    return a


# @api_view(["GET"])
# def get_item_rating(request):
#     post_similarity = []
#     post_list = Post.objects.all()
#     user_list = User.objects.all()
#     vector_list_p2 = []
#     user_list_p2 = []
#     item_list_p2 = []
#     first_vector = []
#     post_id = 140
#     for p in Post.objects.filter(pk=post_id):
#         for user in user_list:
#             rating = UserVote.objects.filter(user=user, post__id=p.id).first()
#             if rating:
#                 first_vector.append(rating.get_rating())
#             if not rating:
#                 first_vector.append(2)
#     count = 0
#     current_vector = [2, 4, 2, 1, 2, 2, 1, 5, 1, 3, 2, 4]
#     for post in post_list:
#         vector = []
#         for user in user_list:

#             rating = UserVote.objects.filter(user=user,
#                                              post__id=post.id).first()
#             if rating:
#                 vector.append(rating.get_rating())
#             if not rating:
#                 vector.append(2)
#                 if post.id == 141:
#                     print("append")
#                     print(vector)
#         count += 1
#         rt_dict = {}
#         print("s", vector)
#         rt_dict["id"] = post.id
#         rt_dict["similarity"] = 1 - spatial.distance.cosine(
#             sum_average_list(first_vector), sum_average_list(vector))
#         post_similarity.append(rt_dict)
#     if len(vector_list_p2) == len(user_list_p2):
#         print("we got what we want lol!")
#     post_similarity.sort(key=lambda item: item.get("similarity"), reverse=True)
#     print("kkk", post_similarity)
#     item_list = []
#     user_list_ = []
#     rating_list = []
#     post_similarity = post_similarity[:5]
#     user_list = User.objects.all()
#     for post in post_similarity:
#         for u in user_list:
#             item_list.append(post["id"])
#             vote = UserVote.objects.filter(user=u, post__id=post["id"]).first()
#             if vote:
#                 rating_list.append(vote.get_rating())
#             if not vote:
#                 rating_list.append(2)
#             user_list_.append(u.id)

#     for p in post_similarity[:4]:
#         post = Post.objects.filter(pk=p["id"]).first()
#         if post:
#             vote_list = post.vote.all()
#             for v in vote_list:
#                 vector_list_p2.append(v.get_rating())
#                 user_list_p2.append(v.user.id)
#                 item_list_p2.append(post.id)
#     print(user_list_p2)
#     print("======================")
#     print(item_list_p2)
#     print("======================")
#     print(vector_list_p2)
#     rating_dict = {
#         "item": item_list_p2,
#         "user": user_list_p2,
#         "rating": vector_list_p2
#     }
#     df = pd.DataFrame(rating_dict)
#     reader = Reader(rating_scale=(1, 5))
#     # Loads Pandas dataframe
#     data = Dataset.load_from_df(df[["user", "item", "rating"]], reader)
#     sim_options = {
#         "name": "cosine",
#         "user_based": False,  # Compute  similarities between items
#     }
#     algo = KNNWithMeans(sim_options=sim_options)
#     trainingSet = data.build_full_trainset()
#     algo.fit(trainingSet)
#     # prediction = algo.predict(4, 22)
#     for c in list(dict.fromkeys(item_list_p2)):
#         print(algo.predict(4, c))
#     # print(prediction.est)
#     return Response({Message.SC_OK}, status=200)


@api_view(["GET"])
def get_item_rating_1(request):
    if request.user.is_authenticated:
        rating_list_p2 = []
        user_list_p2 = []
        item_list_p2 = []
        recommend_list = []
        post_list = Post.objects.all()
        for post in post_list:
            vote_list = post.vote.all()
            for v in vote_list:
                rating_list_p2.append(v.get_rating())
                user_list_p2.append(v.user.id)
                item_list_p2.append(post.id)
        if len(item_list_p2) == len(user_list_p2) == len(rating_list_p2):
            print("we got what we want lol!")
        rating_dict = {
            "item": item_list_p2,
            "user": user_list_p2,
            "rating": rating_list_p2
        }
        df = pd.DataFrame(rating_dict)
        reader = Reader(rating_scale=(1, 5))
        # Loads Pandas dataframe
        data = Dataset.load_from_df(df[["user", "item", "rating"]], reader)
        sim_options = {
            "name": "cosine",
            "user_based": False,  # Compute  similarities between items
        }
        algo = KNNWithMeans(sim_options=sim_options)
        trainingSet = data.build_full_trainset()
        algo.fit(trainingSet)
        prediction = algo.predict(4, 34)
        print(prediction)
        for p in post_list:
            rt_dict = {}
            rt_dict["id"] = p.id
            rt_dict["point"] = algo.predict(request.user.id, p.id).est
            recommend_list.append(rt_dict)
        recommend_list.sort(key=lambda item: item.get("point"), reverse=True)
        print(recommend_list[0:10])
        post_id_list = []
        post_list = []
        post_list_1 = []
        for r in recommend_list[0:10]:
            post_list_1.append(Post.objects.filter(pk=r["id"]).first())
        return get_paginated_queryset_response(post_list_1, request, 10,
                                               ModelName.POST)
    return Response({Message.SC_NO_AUTH}, status=401)
