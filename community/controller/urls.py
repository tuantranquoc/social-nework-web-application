from django.urls import path
from community.controller import rest as community_api

urlpatterns = [
    path('create', community_api.create_community),
    path('', community_api.get_community),
    path('user/list', community_api.get_list_community_by_user),
    path('list', community_api.get_list_community),
    path('action', community_api.community_action),
    path('change/state/<str:community_type>', community_api.change_state),
    path('update/', community_api.community_update_via_react_view),
    path('recommend/<str:community>', community_api.recommend_sub_community),
    path('recommend', community_api.recommend_community),
    path('graph', community_api.community_graph),
    path('mod/action', community_api.community_mod_action),
    path('member/list', community_api.get_member_list),
    path('blacklist', community_api.blacklist),
    path('user/list/<str:username>',
         community_api.get_followed_community_by_username),
]