import random

from rest_framework import serializers

from account.serializers import PublicProfileSerializer
from community.models import Community
from post.models import Post, Comment

MAX_CONTENT_LENGTH = 300


class PostCreateSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)

    class Meta:
        model = Post
        fields = ['user', 'id', 'content', 'timestamp']

    def validate_content(self, value):
        if len(value) > MAX_CONTENT_LENGTH:
            raise serializers.ValidationError("This tweet is too long!")
        return value


class PostSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)
    parent = PostCreateSerializer(read_only=True)
    up_vote = serializers.SerializerMethodField(read_only=True)
    down_vote = serializers.SerializerMethodField(read_only=True)
    community_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['user',
                  'id',
                  'title',
                  'content',
                  'parent',
                  'timestamp',
                  'image', 'timestamp', 'up_vote', 'down_vote', 'community_type', 'view_count']

    def get_up_vote(self, obj):
        return obj.up_vote.count()

    def get_down_vote(self, obj):
        return obj.down_vote.count()

    def get_community_type(self, obj):
        if obj.community:
            return obj.community.community_type
        return None

    def get_sub_community_type(self, obj):
        if obj.sub_community:
            return obj.sub_community.community_type
        return None


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    up_vote = serializers.SerializerMethodField(read_only=True)
    down_vote = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        # ['content']
        fields = ['content', 'username', 'post', 'id', 'up_vote', 'down_vote', 'timestamp']

    def get_username(self, obj):
        return obj.user.username

    def get_up_vote(self, obj):
        return obj.up_vote.count()

    def get_down_vote(self, obj):
        return obj.down_vote.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)
    post = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

    def validate_content(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError("This tweet is too long!")
        return value


class CommunitySerializer(serializers.ModelSerializer):
    #   count = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    community_type = serializers.SerializerMethodField(read_only=True)
    is_main = serializers.SerializerMethodField(read_only=True)
    follower = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Community
        fields = ['id', 'community_type', 'is_main', 'avatar', 'background', 'description', 'follower','timestamp']

    def get_id(self, obj):
        return obj.id

    def get_community_type(self, obj):
        return obj.community_type

    def get_is_main(self, obj):
        if obj.parent is None:
            return "true"
        return "false"

    def get_follower(self, obj):
        if obj.user:
            return obj.user.count()
        return 0
