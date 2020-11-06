from rest_framework import serializers
from .models import Profile


class PublicProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField(read_only=True)
    last_name = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)
    follower_count = serializers.SerializerMethodField(read_only=True)
    following_count = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Profile
        fields = ['first_name',
                  'last_name', 'id',
                  'location',
                  'bio',
                  'follower_count',
                  'following_count',
                  'is_following',
                  'username',
                  'background', 'avatar', 'timestamp', 'email']

    def get_is_following(self, obj):
        is_following = False
        context = self.context
        request = context.get("request")
        if request:
            user = request.user
            is_following = user in obj.follower.all()
        return is_following

    @staticmethod
    def get_follower_count(obj):
        return obj.follower.count()

    @staticmethod
    def get_following_count(obj):
        return obj.user.following.count()

    @staticmethod
    def get_first_name(obj):
        return obj.user.first_name

    @staticmethod
    def get_last_name(obj):
        return obj.user.last_name

    @staticmethod
    def get_username(obj):
        return obj.user.username

    @staticmethod
    def get_email(obj):
        return obj.user.email


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'location']
