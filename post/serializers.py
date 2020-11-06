from rest_framework import serializers

from account.serializers import PublicProfileSerializer
from community.models import Community
from post.models import Post, Comment, PostType

MAX_CONTENT_LENGTH = 300


class PostCreateSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)

    class Meta:
        model = Post
        fields = ['user', 'id', 'content', 'timestamp']

    @staticmethod
    def validate_content(value):
        if len(value) > MAX_CONTENT_LENGTH:
            raise serializers.ValidationError("This content is too long!")
        return value


class PostSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)
    parent = PostCreateSerializer(read_only=True)
    up_vote = serializers.SerializerMethodField(read_only=True)
    down_vote = serializers.SerializerMethodField(read_only=True)
    community_type = serializers.SerializerMethodField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['user',
                  'id',
                  'title',
                  'content',
                  'parent',
                  'timestamp',
                  'image', 'timestamp', 'up_vote', 'down_vote', 'community_type', 'type', 'view_count']

    @staticmethod
    def get_up_vote(obj):
        return obj.up_vote.count()

    @staticmethod
    def get_down_vote(obj):
        return obj.down_vote.count()

    @staticmethod
    def get_community_type(obj):
        if obj.community:
            return obj.community.community_type
        return None

    @staticmethod
    def get_sub_community_type(obj):
        if obj.sub_community:
            return obj.sub_community.community_type
        return None

    @staticmethod
    def get_type(obj):
        if obj.type:
            return obj.type.type
        return None


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    up_vote = serializers.SerializerMethodField(read_only=True)
    down_vote = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['content', 'username', 'post', 'id', 'up_vote', 'down_vote', 'timestamp']

    @staticmethod
    def get_username(obj):
        return obj.user.username

    @staticmethod
    def get_up_vote(obj):
        return obj.up_vote.count()

    @staticmethod
    def get_down_vote(obj):
        return obj.down_vote.count()


class CommentCreateSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(source='user.profile', read_only=True)
    post = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

    @staticmethod
    def validate_content(value):
        if len(value) > 1000:
            raise serializers.ValidationError("This content is too long!")
        return value


class CommunitySerializer(serializers.ModelSerializer):
    #   count = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    community_type = serializers.SerializerMethodField(read_only=True)
    is_main = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)
    follower = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Community
        fields = ['id', 'community_type', 'is_following', 'is_main', 'avatar', 'background', 'description', 'follower',
                  'timestamp', 'rule']

    @staticmethod
    def get_id(obj):
        return obj.id

    @staticmethod
    def get_community_type(obj):
        return obj.community_type

    @staticmethod
    def get_is_main(obj):
        if obj.parent is None:
            return True
        return False

    @staticmethod
    def get_follower(obj):
        if obj.user:
            return obj.user.count()
        return 0

    def get_is_following(self, obj):
        is_following = False
        context = self.context
        request = context.get("request")
        if request:
            user = request.user
            is_following = user in obj.user.all()
        return is_following


class PostTypeSerializer(serializers.ModelSerializer):
    #   count = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostType
        fields = ['id', 'type']

    @staticmethod
    def get_id(obj):
        return obj.id


class CommentGraphSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'timestamp']

    @staticmethod
    def get_id(obj):
        return obj.id


class PostGraphSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'timestamp']

    @staticmethod
    def get_id(obj):
        return obj.id
