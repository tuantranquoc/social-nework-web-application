from django.urls import path
from post.controller.post_controller import rest as post_api

urlpatterns = [
    path('filter/<str:sort>', post_api.post_list_view),
    
    path('create', post_api.post_create_api),
    path('<int:post_id>', post_api.find_post_by_id),
    path('delete/', post_api.post_delete_api),
    path('repost/<int:post_id>', post_api.re_post),
    path('action', post_api.post_action),
    path('count/<str:community_type>', post_api.get_count_by_community),
    path('user', post_api.get_list_post_by_user),
    path('user/<str:username>', post_api.find_post_by_user),
    path('count', post_api.get_post_count),
    path('count/user/<str:username>', post_api.count_post_by_user),
    path('vote/count', post_api.get_count_by_vote),
    path('vote/<int:post_id>', post_api.get_post_vote),
    path('up_vote/count', post_api.get_count_by_up_vote),
    path('down_vote/count', post_api.get_count_by_down_vote),
    path('vote/count/user/<str:username>', post_api.get_count_by_user_vote),
    path('up_vote/count/user/<str:username>',
         post_api.get_count_by_username_up_vote),
    path('down_vote/count/user/<str:username>',
         post_api.get_count_by_username_down_vote),
    path('check/vote', post_api.check_vote),
    path('filter/up_vote', post_api.filter_by_up_vote),
    path('filter/user/up_vote', post_api.get_list_post_by_up_vote),
    path('comment', post_api.get_post_by_comment),
    path('comment/<str:username>', post_api.get_post_by_username_comment),
    path('up_vote', post_api.find_post_by_up_vote),
    path('up_vote/<str:username>', post_api.find_post_by_username_up_vote),
    path('down_vote', post_api.find_post_by_down_vote),
    path('down_vote/<str:username>', post_api.find_post_by_username_down_vote),
    path('trending', post_api.trending),
    path('recent', post_api.recent),
    path('hot', post_api.hot),
    path('type', post_api.get_type_list),
    path('graph', post_api.get_post_by_time_interval),
    path('top', post_api.get_post_by_time_interval),
    path('reset', post_api.reset),
    path('community/<str:community_type>', post_api.find_post_by_community),
    path('recommend', post_api.get_item_rating_1),
    path('profile', post_api.get_post_list_by_following_profile),
    path('collect-data', post_api.collect_post_data),
     path('favorite/list', post_api.get_favorite_list)


]