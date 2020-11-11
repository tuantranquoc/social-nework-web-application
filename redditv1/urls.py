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
from django.urls import path, include
from post.controller.post_controller import rest as post_api
from post.controller.comment_controller import rest as comment_api
from account.controller import rest as profile_api
from community.controller import rest as community_api
from rest_framework_simplejwt import views as jwt_views
from chat.controller import rest as chat_api
from account.controller import rest as profile_api
from redditv1 import settings
import account

urlpatterns = [
    # admin urls
    path('admin/', admin.site.urls),
    # post api
    path('api/post/', include('post.controller.post_controller.urls')),
    # 31
    # comment api
    path('api/comment/', include('post.controller.comment_controller.urls')),
    # 11
    # profile api
    path('api/profile/', include('account.controller.urls')),
    # 10
    # community api
    path('api/community/', include('community.controller.urls')),
    # 7
    # char api
    path('api/chatroom/create/<str:username>', chat_api.create_chat_room),
    path('api/chatroom/chat/<str:username>', chat_api.create_chat),
    path('api/chatroom/view/<str:username>', chat_api.get_chat_view),
    # 6
    # token
    path('api/search/', profile_api.search),
    path('api/token/',
         jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/',
         jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/login', profile_api.login_via_react_view),
    path('api/logout', profile_api.logout_view_js),
]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
