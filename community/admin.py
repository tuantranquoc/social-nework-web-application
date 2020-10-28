from django.contrib import admin

# Register your models here.
from .models import Community


class CommunityAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__str__', '__creator__', '__user_count__', '__state__']

    class Meta:
        model = Community


admin.site.register(Community, CommunityAdmin)
