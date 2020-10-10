from django.urls import path
from ..api import views

urlpatterns = [
    # Views
    path('<str:username>/follow', views.profile_detail_api_view),
]