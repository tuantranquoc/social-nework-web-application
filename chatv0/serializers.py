from .models import Room
from rest_framework import serializers
from account.serializers import PublicProfileSerializer, ChatProfileSerializer
from chatv0.models import Message


class RoomSerializer(serializers.ModelSerializer):
    lasted_message = serializers.SerializerMethodField(read_only=True)
    user_list = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Room
        fields = ['id','lasted_message','user_list']
    @staticmethod
    def get_lasted_message(obj):
        lasted_message = Message.objects.filter(room__id=obj.id).order_by("-created_at").first()
        if lasted_message:
            return lasted_message.content
        return None

    def get_user_list(self, obj):
        request = self.context.get("request")
        if request.user:
            user_list = obj.user.all()
            if user_list:
                u_l = []
                for u in user_list:
                    if u != request.user:
                        u_l.append({"username":u.username,"avatar": u.profile.avatar.url or None})
                return u_l
        return None
