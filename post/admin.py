from django.contrib import admin

# Register your models here.
from .models import Post, PositivePoint, Comment, PostType, View, CommentPoint, UserVote


class PostAdmin(admin.ModelAdmin):
    search_fields = ['id']

    list_display = [
        '__id__', '__title__', '__community__', '__user__', '__up_vote__', '__down_vote__',
       '__type__', '__view__', '__point__','__state__','hidden','hidden_in_community', '__time__'
      
    ]
    # list_display = ('id',)

    class Meta:
        model = Post


class PositivePointAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__str__', '__point__']

    class Meta:
        model = PositivePoint


class CommentAdmin(admin.ModelAdmin):
    list_display = [
        '__id__', '__str__', '__user__', '__parent__', '__up_vote__',
        '__down_vote__', '__timestamp__', '__post__', '__point__', '__level__',
        '__parent__', '__state__'
    ]

    class Meta:
        model = Comment


class CommentPointAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__point__']

    class Meta:
        model = CommentPoint


class PostTypeAdmin(admin.ModelAdmin):
    list_display = ['__str__']

    class Meta:
        model = PostType


class ViewAdmin(admin.ModelAdmin):
    list_display = ['__user__', '__old_timestamp__']

    class Meta:
        model = View
        
@admin.register(UserVote)
class UserVoteAdmin(admin.ModelAdmin):
    search_fields = ['id']
    list_display = ['id', 'user','post', 'report','view','like','share','dislike','get_rating']


admin.site.register(Post, PostAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(PostType, PostTypeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentPoint, CommentPointAdmin)
