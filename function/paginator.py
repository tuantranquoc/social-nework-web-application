from rest_framework.pagination import PageNumberPagination
from post.serializers import CommentSerializer, CommunitySerializer, PostSerializer, PostGraphSerializer, CommentGraphSerializer, CommunityGraphSerializer, PostTypeSerializer
from redditv1.name import ModelName
from notify.serializers import SignalRoomSerializer, NotificationSerializer, UserNotifySerializers
from account.serializers import ProfileSerializer, PublicProfileSerializer
from chatv0.serializers import RoomSerializer
from requests.models import Response
from typing import OrderedDict
from rest_framework import pagination
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination


def get_paginated_queryset_response(query_set, request, page_size, model):
    paginator = PageNumberPagination()
    if not page_size:
        page_size = 10
    paginator.page_size = page_size
    paginated_qs = paginator.paginate_queryset(query_set, request)
    if model == ModelName.COMMUNITY:
        serializer = CommunitySerializer(paginated_qs,
                                         many=True,
                                         context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.COMMUNITY_GRAPH:
        serializer = CommunityGraphSerializer(paginated_qs,
                                              many=True,
                                              context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.PROFILE:
        serializer = PublicProfileSerializer(paginated_qs,
                                             many=True,
                                             context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.POST:
        serializer = PostSerializer(paginated_qs,
                                    many=True,
                                    context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.COMMENT:
        serializer = CommentSerializer(paginated_qs,
                                       many=True,
                                       context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.COMMENT_GRAPH:
        serializer = CommentGraphSerializer(paginated_qs,
                                            many=True,
                                            context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.POST_TYPE:
        serializer = PostTypeSerializer(paginated_qs,
                                        many=True,
                                        context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.POST_GRAPH:
        serializer = PostGraphSerializer(paginated_qs,
                                         many=True,
                                         context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.CHAT:
        serializer = RoomSerializer(paginated_qs,
                                         many=True,
                                         context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.SIGNAL_ROOM:
        serializer = SignalRoomSerializer(paginated_qs,
                                         many=True,
                                         context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.NOTIFICATION:
        serializer = NotificationSerializer(paginated_qs,
                                         many=True,
                                         context={"request": request})
        return paginator.get_paginated_response(serializer.data)
    elif model == ModelName.USER_NOTIFY:
        # serializer = UserNotifySerializers(paginated_qs,
        #                                  many=True,
        #                                  context={"request": request})
        # return get_paginated_response(PageNumberPagination,  serializer.data,1)
        # page = paginator.paginate_queryset(query_set)
        serializer_class = UserNotifySerializers(paginated_qs, many=True,)
        return pagination.get_paginated_response(serializer_class.data)




class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })