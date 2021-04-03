from django.contrib import admin
from .models import Notification, NotificationChange, NotificationObject, EntityType, SignalRoom, UserNotify, CommunityNotify


# Register your models here.
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['__id__', 'created_at']

    class Meta:
        model = Notification


class NotificationChangeAdmin(admin.ModelAdmin):
    list_display = ['__id__', 'created_at']

    class Meta:
        model = NotificationChange


class NotificationObjectAdmin(admin.ModelAdmin):
    list_display = ['__id__', 'created_at']

    class Meta:
        model = NotificationObject


class EntityTypeAdmin(admin.ModelAdmin):
    list_display = ['__id__', 'description', 'created_at', 'notify_message']

    class Meta:
        model = EntityType


class SignalRoomTypeAdmin(admin.ModelAdmin):
    list_display = ['__id__', 'str']

    class Meta:
        model = SignalRoom
        
class UserNotifyAdmin(admin.ModelAdmin):
    list_display = ['__id__', 'username', 'created_at']

    class Meta:
        model = UserNotify
        

class CommunityNotifyAdmin(admin.ModelAdmin):
    list_display = ['__id__', 'community', 'created_at']

    class Meta:
        model = CommunityNotify



admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationChange, NotificationChangeAdmin)
admin.site.register(NotificationObject, NotificationObjectAdmin)
admin.site.register(EntityType, EntityTypeAdmin)
admin.site.register(SignalRoom, SignalRoomTypeAdmin)
admin.site.register(UserNotify, UserNotifyAdmin)
admin.site.register(CommunityNotify, CommunityNotifyAdmin)