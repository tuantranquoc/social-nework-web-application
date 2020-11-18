from django.contrib import admin
from .models import CommunityTrack, Track


# Register your models here.
class TrackAdmin(admin.ModelAdmin):
    list_display = [
        '__id__',
        '__user__',
        '__community__',
    ]

    class Meta:
        model = Track

class CommunityTrackAdmin(admin.ModelAdmin):
    list_display = [
        '__id__',
        '__community__',
        '__timestamp__'
    ]

    class Meta:
        model = CommunityTrack

admin.site.register(Track, TrackAdmin)
admin.site.register(CommunityTrack, CommunityTrackAdmin)