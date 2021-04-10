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
User = get_user_model()


@api_view(["GET", "POST"])
def post_list_view(request):
    return post_service.get_post_list(request)


@api_view(["POST"])
def post_create_api(request):
    """
    .. code-block:: Example post submit

         {
             "title": new title,
             "content": hello world,
             "community": "anime",
             "type":"content"
             "image":"base64"
         }
    """
    return post_service.create_post(request)


@api_view(["POST"])
def post_delete_api(request):
    """
    data = {"id":"post_id"}
    """
    return post_service.delete_post(request)


@api_view(["GET"])
def find_post_by_id(request, post_id):
    """
    ``GET`` lists all relations where an ``Organization`` is accessible by
     a ``User``. Typically the user was granted specific permissions through
     a ``Role``.

    ``POST`` Generates a request to attach a user to a role on an organization

     see :doc:`Flexible Security Framework `.

     **Example request**:

    .. code-block:: http

        GET  /api/users/alice/accessibles/

    **Example response**:

    .. code-block:: json

         {
             "count": 1,
             "previous": null,
             "results": [
                 {
                    "created_at": "2018-01-01T00:00:00Z",
                     "slug": "cowork",
                     "printable_name": "ABC Corp.",
                     "role_description": "manager",
                  }
             ]
         }
    """
    return post_service.find_post_by_id(request, post_id)


@api_view(["POST", "GET"])
def re_post(request, post_id):
    return post_service.re_post(request, post_id)


@api_view(["POST"])
def post_action(request):
    return post_service.action(request)


@api_view(["GET"])
def get_list_post_by_user(request):
    return post_service.find_post_by_user(request)


@api_view(["GET"])
def get_list_post_by_up_vote(request):
    """
    data = {"page_size":"page_size"}
    """
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def user_comment_post(request):
    if request.user.is_authenticated:
        comment = Comment.objects.filter(user=request.user)
        # return get_paginated_queryset_response(query, request)
    return Response({Message.SC_NO_AUTH}, status=401)


@api_view(["GET"])
def get_count_by_community(request, community_type):
    return Response({"Total": count_post_by_community(community_type)})


@api_view(["GET"])
def get_post_count(request):
    count = Post.objects.filter(user=request.user).count()
    return Response({"Total": count})


@api_view(["GET"])
def get_comment_count(request):
    count = Comment.objects.filter(user=request.user).count()
    return Response({"Total": count})


@api_view(["GET"])
def get_count_by_vote(request):
    up_vote_count = Post.objects.filter(up_vote=request.user).count()
    down_vote_count = Post.objects.filter(down_vote=request.user).count()
    return Response({"Total": up_vote_count + down_vote_count})


@api_view(["GET"])
def get_count_by_up_vote(request):
    up_vote_count = Post.objects.filter(up_vote=request.user).count()
    return Response({"Total": up_vote_count})


@api_view(["GET"])
def get_count_by_username_up_vote(request, username):
    up_vote_count = Post.objects.filter(up_vote__username=username).count()
    return Response({"Total": up_vote_count})


@api_view(["GET"])
def get_count_by_down_vote(request):
    down_vote_count = Post.objects.filter(down_vote=request.user).count()
    return Response({"Total": down_vote_count})


@api_view(["GET"])
def get_count_by_username_down_vote(request, username):
    down_vote_count = Post.objects.filter(down_vote__username=username).count()
    return Response({"Total": down_vote_count})


@api_view(["GET"])
def get_count_by_user_vote(request, username):
    up_vote_count = Post.objects.filter(up_vote__username=username).count()
    down_vote_count = Post.objects.filter(down_vote__username=username).count()
    return Response({"Total": up_vote_count + down_vote_count})


@api_view(["POST"])
def check_vote(request):
    if request.user.is_authenticated:
        post_id = request.data.get('id')
        if Post.objects.filter(up_vote=request.user, id=post_id):
            return Response({"up_vote"})
        if Post.objects.filter(down_vote=request.user, id=post_id):
            return Response({"down_vote"})
    return Response({"none"})


@api_view(["GET", "POST"])
def filter_by_up_vote(request):
    page_size = request.data.get("page_size")
    query = Post.objects.annotate(
        user_count=Count("up_vote")).order_by("-user_count").filter(
            community__state=True)
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.POST)


@api_view(["GET"])
def get_post_by_comment(request):
    return post_service.find_post_by_comment(request)


@api_view(["GET"])
def get_post_by_username_comment(request, username):
    return post_service.find_post_by_comment_with_username(request, username)


@api_view(["GET"])
def find_post_by_user(request, username):
    page_size = request.data.get("page_size")
    post = Post.objects.filter(user__username=username, community__state=True)
    if post:
        return get_paginated_queryset_response(post, request, page_size,
                                               ModelName.POST)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET"])
def count_post_by_user(request, username):
    count = Post.objects.filter(user__username=username).count()
    if count:
        return Response({"Total": count}, status=200)
    return Response({Message.SC_NOT_FOUND}, status=400)


@api_view(["GET"])
def find_post_by_up_vote(request):
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def find_post_by_username_up_vote(request, username):
    return post_service.find_post_by_username_up_vote(request, username)


@api_view(["GET"])
def find_post_by_down_vote(request):
    return post_service.find_post_by_up_vote(request)


@api_view(["GET"])
def find_post_by_username_down_vote(request, username):
    return post_service.find_post_by_username_down_vote(request, username)


@api_view(['GET', 'POST'])
def trending(request, days):
    return post_service.trending(request, days)


@api_view(['GET', 'POST'])
def hot(request):
    return post_service.hot(request)


@api_view(['GET', 'POST'])
def recent(request):
    return post_service.recent(request)


@api_view(['GET'])
def get_type_list(request):
    page_size = request.data.get("page_size")
    query = PostType.objects.all()
    return get_paginated_queryset_response(query, request, page_size,
                                           ModelName.POST_TYPE)


@api_view(["POST", "GET"])
def get_post_by_time_interval(request):
    """
    data = {"from_timestamp":"from_timestamp","to_timestamp":"to_timestamp","page_size":"page_size","type":"type"}
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
        rt_dict["point"] = algo.predict(16, p.id).est
        recommend_list.append(rt_dict)
    recommend_list.sort(key=lambda item: item.get("point"), reverse=True)
    print(recommend_list)
    return Response({Message.SC_OK}, status=200)
