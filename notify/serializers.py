from .models import SignalRoom, Notification
from rest_framework import serializers


class SignalRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalRoom
        fields = ['id']
        
        

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id']
