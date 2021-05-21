from django.contrib import admin

# Register your models here.
from .models import Community, CommunityHistory, Member, MemberInfo, CommunityBlackList, BlackListType


class CommunityAdmin(admin.ModelAdmin):
    list_display = [
        '__id__', '__str__', '__creator__', '__user_count__', '__state__',
        '__description__', '__rule__', '__color__', '__mod__'
    ]

    class Meta:
        model = Community


class CommunityHistoryAdmin(admin.ModelAdmin):
    list_display = [
        '__id__', '__community__', '__change_by__', '__target__',
        '__old_role__', '__new_role__', '__timestamp__'
    ]

    class Meta:
        model = CommunityHistory


class MemberAdmin(admin.ModelAdmin):
    list_display = ['__id__', '__user__', '__community__']

    class Meta:
        model = Member


class MemberInfoAdmin(admin.ModelAdmin):
    search_fields = ['community__community_type', 'member__user__username']
    list_display = [
        '__id__','member_name','member_id', '__community__', '__timestamp__', '__state__', '__role__',
    ]

    class Meta:
        model = MemberInfo


class CommunityBlackListAdmin(admin.ModelAdmin):
    list_display = ['__str__', '__community__','__user__']

    class Meta:
        model = CommunityBlackList


class BlackListTypeAdmin(admin.ModelAdmin):
    list_display = [
        '__str__',
        '__description__',
    ]

    class Meta:
        model = BlackListType


admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityHistory, CommunityHistoryAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(MemberInfo, MemberInfoAdmin)
admin.site.register(CommunityBlackList, CommunityBlackListAdmin)
admin.site.register(BlackListType, BlackListTypeAdmin)
