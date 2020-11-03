from django.contrib import admin

# Register your models here.
from chat.models import ChatRoom


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['__id__','__count__']

    class Meta:
        model = ChatRoom


admin.site.register(ChatRoom, ChatRoomAdmin)