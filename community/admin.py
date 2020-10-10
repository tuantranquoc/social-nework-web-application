from django.contrib import admin

# Register your models here.
from .models import Community, SubCommunity


class CommunityAdmin(admin.ModelAdmin):
    list_display = ['__str__', '__id__']

    class Meta:
        model = Community


class SubCommunityAdmin(admin.ModelAdmin):
    list_display = ['__str__', '__id__','__timestamp__','__parent__','__sub_parent__']

    class Meta:
        model = SubCommunity


admin.site.register(Community, CommunityAdmin)
admin.site.register(SubCommunity, SubCommunityAdmin)
