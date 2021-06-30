from .models import SignalRoom, Notification, UserNotify
from rest_framework import serializers
from notify.models import NotificationChange
from post.serializers import CommunitySerializer
from community.models import Community


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
    entity_id = serializers.SerializerMethodField(read_only=True)
    message =  serializers.SerializerMethodField(read_only=True)
    community = serializers.SerializerMethodField(read_only=True)
    # title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserNotify
        fields = ['id', 'message', 'status','user', 'type','entity_id','community']

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
                title = "new_post"
                return title
        return None

    @staticmethod
    def get_entity_id(obj):
        for x in obj.notification_object.all():
            if x.post:
                return x.post.id
        return None
    
    @staticmethod
    def get_message(obj):
        for x in obj.notification_object.all():
            if x.entity_type.id == 4:
                title = x.post.title
                return title
            if x.entity_type.id == 6:
                title = x.post.title
                return title
        return None
    
    @staticmethod
    def get_community(obj):
        for x in obj.notification_object.all():
            if x.entity_type.id == 6:
                community = x.post.community
                print(community)
                community = Community.objects.filter(community_type=community).first()
                if community:
                    if community.avatar:
                        return {"community_type":community.community_type,"avatar":community.avatar.url}
                return {"community_type":community.community_type,"avatar":None}

            return None
 

