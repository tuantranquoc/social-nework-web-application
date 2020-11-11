from django.urls import path
from account.controller import rest as profile_api

urlpatterns = [
    path('', profile_api.profile_current_detail_view),
    path('<str:username>', profile_api.profile_detail_view),
    path('api/register', profile_api.register_via_react_view),
    path('update/', profile_api.profile_update_via_react_view),
    path('action/', profile_api.profile_action),
    path('recommend/global', profile_api.recommend_user_from_global),
    path('recommend/feed', profile_api.recommend_user_from_feed),
    path('recommend/profile/<str:username>',
         profile_api.recommend_user_from_profile),
]