from rest_framework.pagination import PageNumberPagination
from post.serializers import CommentSerializer, CommunitySerializer, PostSerializer, PostGraphSerializer, CommentGraphSerializer, CommunityGraphSerializer, PostTypeSerializer
from redditv1.name import ModelName
from account.serializers import ProfileSerializer, PublicProfileSerializer


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