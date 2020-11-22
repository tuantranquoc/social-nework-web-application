from rest_framework import serializers

from account.serializers import PublicProfileSerializer
from community.models import Community, Member, MemberInfo
from post.models import Post, Comment, PostType
from redditv1.name import CommentState, ImagePath, Role
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
    point = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'user', 'id', 'title', 'content', 'parent', 'timestamp', 'image',
            'timestamp', 'up_vote', 'down_vote', 'community_type', 'type',
            'view_count', 'point', 'state'
        ]

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

    @staticmethod
    def get_point(obj):
        return "%.2f" % obj.point

    def get_content(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        # user =  self.context['request'].user
        if obj.state == CommentState.PUBLIC:
            return obj.content
        if obj.state == CommentState.HIDDEN:
            if obj.community.creator == user:
                return obj.content
            member = Member.objects.filter(user=user).first()
            member_info = MemberInfo.objects.filter(
                member=member, community=obj.community).first()
            if member_info:
                if member_info.role == Role.MOD:
                    return obj.content
            return ["HIDDEN"]
        if obj.state == CommentState.DELETED:
            return ["Post has been delete by owner"]

    def get_image(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if obj.state == CommentState.PUBLIC:
            if obj.image:
                return obj.image.url
        if obj.state == CommentState.HIDDEN:
            if obj.image:
                if obj.community.creator == user:
                    return obj.image.url
            return ImagePath.REMOVED
        if obj.state == CommentState.DELETED:
            return ImagePath.REMOVED


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    up_vote = serializers.SerializerMethodField(read_only=True)
    down_vote = serializers.SerializerMethodField(read_only=True)
    parent = serializers.SerializerMethodField(read_only=True)
    point = serializers.SerializerMethodField(read_only=True)
    content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'content', 'username', 'post', 'parent', 'id', 'up_vote',
            'down_vote', 'timestamp', 'point', 'level', 'state'
        ]

    @staticmethod
    def get_username(obj):
        return obj.user.username

    @staticmethod
    def get_up_vote(obj):
        return obj.up_vote.count()

    @staticmethod
    def get_down_vote(obj):
        return obj.down_vote.count()

    @staticmethod
    def get_point(obj):
        return "%.2f" % obj.point

    @staticmethod
    def get_parent(obj):
        if obj.parent:
            return obj.parent.id
        return None

    def get_content(self, obj):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        post = find_post_by_comment(obj)
        if obj.state == CommentState.PUBLIC:
            return obj.content
        if obj.state == CommentState.HIDDEN:
            if post.community.creator == user:
                return obj.content
            return ["HIDDEN"]
        if obj.state == CommentState.DELETED:
            return ["Comment has been delete by owner"]


def find_post_by_comment(comment):
    if comment:
        while comment.parent:
            comment = comment.parent
        return comment.post


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
    member_count = serializers.SerializerMethodField(read_only=True)
    id = serializers.SerializerMethodField(read_only=True)
    community_type = serializers.SerializerMethodField(read_only=True)
    is_main = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)
    follower = serializers.SerializerMethodField(read_only=True)
    parent = serializers.SerializerMethodField(read_only=True)
    is_creator = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Community
        fields = [
            'id', 'community_type', 'parent', 'is_following', 'is_main',
            'is_creator', 'avatar', 'background', 'description', 'follower',
            'timestamp', 'rule', 'member_count', 'background_color',
            'title_background_color', 'description_background_color',
            'button_background_color', 'button_text_color', 'text_color',
            'post_background_color'
        ]

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

    @staticmethod
    def get_member_count(obj):
        return obj.user.all().count()

    @staticmethod
    def get_parent(obj):
        if obj.parent:
            return obj.parent.community_type
        return None

    def get_is_creator(self, obj):
        user = None
        request = self.context.get("request")
        if obj.creator == request.user:
            return True
        return False


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


class CommunityGraphSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Community
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
