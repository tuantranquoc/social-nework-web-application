from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from account.models import Profile
from account.serializers import PublicProfileSerializer


@api_view(["GET"])
def profile_list_view(request):
    profiles = Profile.objects.all()
    return get_paginated_queryset_recommend_user_response(profiles, request)


def get_paginated_queryset_recommend_user_response(query_set, request):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_qs = paginator.paginate_queryset(query_set, request)
    serializer = PublicProfileSerializer(paginated_qs, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def profile_detail_view(request, username):
    profiles = Profile.objects.filter(user__username=username)
    return get_paginated_queryset_recommend_user_response(profiles, request)
