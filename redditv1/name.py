class ModelName:
    COMMUNITY = "Community"
    USER = "User"
    COMMENT = "Comment"
    CHAT = "CHAT"
    POSITIVE_POINT = "Positive point"
    VIEW = "View"
    PROFILE = "Profile"
    POST = "Post"
    COMMUNITY_GRAPH = "Community graph"
    COMMENT_GRAPH = "Comment graph"
    POST_TYPE = "Post type"
    POST_GRAPH = "Post graph"
    SIGNAL_ROOM = "Signal room"
    NOTIFICATION = "Notification"


class CommentState:
    PUBLIC = 'public'
    HIDDEN = 'hidden'
    DELETED = 'deleted'


class ImagePath:
    REMOVED = '/media/removed.png'


class Role:
    MEMBER = 'MEMBER'
    ADMIN = 'ADMIN'
    MOD = 'MOD'


class BLType:
    BLOCK = 'BLOCK'
    VIEW_ONLY = 'VIEW_ONLY'