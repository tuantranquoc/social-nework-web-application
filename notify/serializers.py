from .models import SignalRoom, Notification, UserNotify
from rest_framework import serializers
from notify.models import NotificationChange


class SignalRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalRoom
        fields = ['id']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id']


class UserNotifySerializers(serializers.ModelSerializer):
    user = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserNotify
        fields = ['id', 'message', 'status','user', 'type']

    @staticmethod
    def get_user(obj):
        for x in obj.notification_object.all():
            nc = NotificationChange.objects.filter(notification_object=x).first()
            if nc:
                if nc.user.profile.avatar:
                    return {"username":nc.user.username,"avatar":nc.user.profile.avatar.url}
            return None

    @staticmethod
    def get_type(obj):
        for x in obj.notification_object.all():
            print(x.entity_type.id)
            if x.entity_type.id == 4:
                return "new_comment"
            if x.entity_type.id == 6:
                return "new_post"
        return None
 
 

