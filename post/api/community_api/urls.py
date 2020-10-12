from django.urls import path
from post.api.post_api import views

urlpatterns = [
    # Views
    path('/post', views.post_list_view),
]