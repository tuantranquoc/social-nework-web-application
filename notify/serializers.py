from .models import SignalRoom, Notification, UserNotify
from rest_framework import serializers


class SignalRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalRoom
        fields = ['id']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id']


class UserNotifySerializers(serializers.ModelSerializer):
    class Meta:
        model = UserNotify
        fields = ['id', 'message', 'status']
