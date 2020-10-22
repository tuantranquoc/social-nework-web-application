from django.contrib import admin

# Register your models here.
from .models import Post, PositivePoint, Comment


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__str__', '__up_vote__', '__down_vote__', '__time__']

    class Meta:
        model = Post


class PositivePointAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__str__', '__point__']

    class Meta:
        model = PositivePoint


class CommentAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__str__', '__user__','__parent__','__up_vote__','__down_vote__','__timestamp__']

    class Meta:
        model = Comment


admin.site.register(Post, ProfileAdmin)
admin.site.register(Comment, CommentAdmin)

