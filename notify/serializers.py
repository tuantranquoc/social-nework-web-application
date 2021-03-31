from .models import SignalRoom
from rest_framework import serializers


class SignalRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignalRoom
        fields = ['id']
