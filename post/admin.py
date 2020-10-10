from django.contrib import admin

# Register your models here.
from .models import Post


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__str__', '__up_vote__', '__time__']

    class Meta:
        model = Post


admin.site.register(Post, ProfileAdmin)
