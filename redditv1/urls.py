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
from django.contrib import admin
from django.urls import path
from post.api.post_api import views as post_api_view
from post.api.comment_api import views as comment_api_view
from account.api import views as profile_api_view
from rest_framework_simplejwt import views as jwt_views

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
    path('api/post/count', post_api_view.get_post_count),
    path('api/post/vote/count', post_api_view.get_count_by_vote),
    path('api/post/check/vote', post_api_view.check_vote),

    # comment api
    path('api/comment/<int:post_id>', comment_api_view.comment_api_view),
    path('api/comment/create/', comment_api_view.comment_create_view),
    path('api/comment/parent/<int:comment_id>', comment_api_view.comment_parent_list_view),
    path('api/comment/child/create/<int:comment_id>', comment_api_view.child_comment_create_view),
    path('api/comment/action', comment_api_view.comment_action),
    path('api/comment/count', post_api_view.get_comment_count),
    path('api/comment/comment/<int:comment_id>', comment_api_view.get_comment_by_id),
    path('api/comment/check/vote', comment_api_view.check_vote),

    # profile api
    path('api/profiles', profile_api_view.profile_list_view),
    path('api/profile', profile_api_view.profile_current_detail_view),
    path('api/profile/<str:username>', profile_api_view.profile_detail_view),
    path('api/login', profile_api_view.login_via_react_view),
    path('api/logout', profile_api_view.logout_view_js),
    path('api/register', profile_api_view.register_via_react_view),

    # token
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]

# urlpatterns += staticfiles_urlpatterns()
#
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL,
#                           document_root=settings.MEDIA_ROOT)
