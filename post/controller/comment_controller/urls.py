from django.urls import path
from post.controller.comment_controller import rest as comment_api
from post.controller.post_controller import rest as post_api
urlpatterns = [
    path('<int:post_id>', comment_api.comment_api_view),
    path('create/', comment_api.comment_create_view),
    path('delete', comment_api.delete_comment),
    path('parent/<int:comment_id>', comment_api.comment_parent_list_view),
    path('child/create/<int:comment_id>',
         comment_api.child_comment_create_view),
    path('action', comment_api.comment_action),
    path('count', post_api.get_comment_count),
    path('count/<str:username>', comment_api.count_by_user_post),
    path('comment/<int:comment_id>', comment_api.get_comment_by_id),
    path('check/vote', comment_api.check_vote),
    path('<int:post_id>/count', comment_api.count_comment_by_post),
    path('graph', comment_api.get_comment_by_time_interval),
    path('reset', comment_api.reset),
    path('update', comment_api.update_comment_level),
    path('parent/<int:comment_id>/count', comment_api.count_comment_by_comment_parent),
]