from .models import Room
from rest_framework import serializers
from account.serializers import PublicProfileSerializer, ChatProfileSerializer
from chatv0.models import Message


class RoomSerializer(serializers.ModelSerializer):
    user = ChatProfileSerializer(read_only=True, many=True)
    lasted_message = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Room
        fields = ['id','user','lasted_message']

    @staticmethod
    def get_lasted_message(obj):
        lasted_message = Message.objects.filter(room__id=obj.id).order_by("-created_at").first()
        if lasted_message:
            return lasted_message.content
        return None
        
