from django.urls import path

from trojstenid.users.views_api import (
    UserDetailView,
    UserListView,
)

app_name = "api"

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:id>/", UserDetailView.as_view(), name="user-detail-id"),
    path(
        "users/<str:username>/", UserDetailView.as_view(), name="user-detail-username"
    ),
]
