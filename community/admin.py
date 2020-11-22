from django.contrib import admin

# Register your models here.
from .models import Community, CommunityHistory, Member, MemberInfo


class CommunityAdmin(admin.ModelAdmin):
    list_display = [
        '__id__', '__str__', '__creator__', '__user_count__', '__state__',
        '__description__', '__rule__', '__color__', '__mod__'
    ]

    class Meta:
        model = Community


class CommunityHistoryAdmin(admin.ModelAdmin):
    list_display = [
        '__id__', '__community__', '__change_by__','__target__','__old_role__','__new_role__', '__timestamp__'
    ]

    class Meta:
        model = CommunityHistory


class MemberAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__user__', '__community__']

    class Meta:
        model = Member


class MemberInfoAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__community__', '__timestamp__','__state__','__role__']

    class Meta:
        model = MemberInfo


admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityHistory, CommunityHistoryAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(MemberInfo, MemberInfoAdmin)
