"""redditv1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from post.api.post_api import views as post_api_view
from post.api.comment_api import views as comment_api_view
from account.api import views as profile_api_view
from community.api import views as community_api_view
from rest_framework_simplejwt import views as jwt_views
from chat.api import views as chat_api_view
from redditv1 import settings

urlpatterns = [
    # admin urls
    path('admin/', admin.site.urls),
    # post api
    path('api/post', post_api_view.post_list_view),
    path('api/post/create', post_api_view.post_create_api),
    path('api/post/<int:post_id>', post_api_view.post_find_by_id),
    path('api/post/delete/<int:post_id>', post_api_view.post_delete_api),
    path('api/post/repost/<int:post_id>', post_api_view.re_post),
    path('api/post/action', post_api_view.post_action),
    path('api/post/count/<str:community_type>', post_api_view.get_count_by_community),
    path('api/post/user', post_api_view.user_post),
    path('api/post/user/<str:username>', post_api_view.find_post_by_user),
    path('api/post/count', post_api_view.get_post_count),
    path('api/post/count/user/<str:username>', post_api_view.count_post_by_user),
    path('api/post/vote/count', post_api_view.get_count_by_vote),
    path('api/post/up_vote/count', post_api_view.get_count_by_up_vote),
    path('api/post/down_vote/count', post_api_view.get_count_by_down_vote),
    path('api/post/vote/count/user/<str:username>', post_api_view.get_count_by_user_vote),
    path('api/post/up_vote/count/user/<str:username>', post_api_view.get_count_by_username_up_vote),
    path('api/post/down_vote/count/user/<str:username>', post_api_view.get_count_by_username_down_vote),
    path('api/post/check/vote', post_api_view.check_vote),
    path('api/post/filter/up_vote', post_api_view.filter_by_up_vote),
    path('api/post/filter/user/up_vote', post_api_view.user_post_filter_by_up_vote),
    path('api/post/comment', post_api_view.get_post_by_comment),
    path('api/post/comment/<str:username>', post_api_view.get_post_by_username_comment),
    path('api/post/up_vote', post_api_view.find_post_by_up_vote),
    path('api/post/up_vote/<str:username>', post_api_view.find_post_by_username_up_vote),
    path('api/post/down_vote', post_api_view.find_post_by_down_vote),
    path('api/post/down_vote/<str:username>', post_api_view.find_post_by_username_down_vote),
    path('api/post/trending/<int:days>', post_api_view.trending),
    path('api/post/recent', post_api_view.recent),
    path('api/post/hot', post_api_view.hot),
    path('api/post/type', post_api_view.get_type_list),
    path('api/post/graph', post_api_view.get_post_by_time_interval),
    path('api/post/reset', post_api_view.reset),
    # 31
    # comment api
    path('api/comment/<int:post_id>', comment_api_view.comment_api_view),
    path('api/comment/create/', comment_api_view.comment_create_view),
    path('api/comment/parent/<int:comment_id>', comment_api_view.comment_parent_list_view),
    path('api/comment/child/create/<int:comment_id>', comment_api_view.child_comment_create_view),
    path('api/comment/action', comment_api_view.comment_action),
    path('api/comment/count', post_api_view.get_comment_count),
    path('api/comment/count/<str:username>', comment_api_view.count_by_user_post),
    path('api/comment/comment/<int:comment_id>', comment_api_view.get_comment_by_id),
    path('api/comment/check/vote', comment_api_view.check_vote),
    path('api/comment/<int:post_id>/count', comment_api_view.count_comment_by_post),
    path('api/comment/graph', comment_api_view.get_comment_by_time_interval),
    path('api/comment/reset', comment_api_view.reset),
    # 11
    # profile api
    path('api/profiles', profile_api_view.profile_list_view),
    path('api/profile', profile_api_view.profile_current_detail_view),
    path('api/profile/<str:username>', profile_api_view.profile_detail_view),
    path('api/login', profile_api_view.login_via_react_view),
    path('api/logout', profile_api_view.logout_view_js),
    path('api/register', profile_api_view.register_via_react_view),
    path('api/profile/update/', profile_api_view.profile_update_via_react_view),
    path('api/profile/action/', profile_api_view.profile_action),
    path('api/profile/recommend/global', profile_api_view.recommend_user_from_global),
    path('api/profile/recommend/feed', profile_api_view.recommend_user_from_feed),
    path('api/profile/recommend/profile/<str:username>', profile_api_view.recommend_user_from_profile),
    # 10
    # community api
    path('api/community/create', community_api_view.create_community),
    path('api/community', community_api_view.get_community),
    path('api/community/user/list', community_api_view.get_list_community_by_user),
    path('api/community/list', community_api_view.get_list_community),
    path('api/community/action', community_api_view.community_action),
    path('api/community/change/state/<str:community_type>', community_api_view.change_state),
    path('api/community/update/', community_api_view.community_update_via_react_view),
    path('api/community/recommend/<str:community>', community_api_view.recommend_sub_community),
    path('api/community/recommend', community_api_view.recommend_community),
    # 7
    # char api
    path('api/chatroom/create/<str:username>', chat_api_view.create_chat_room),
    path('api/chatroom/chat/<str:username>', chat_api_view.create_chat),
    path('api/chatroom/view/<str:username>', chat_api_view.get_chat_view),
    # 6
    # token
    path('api/search/', profile_api_view.search),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
