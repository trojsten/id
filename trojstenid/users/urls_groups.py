from django.urls import path

from trojstenid.users.views import GroupListView, GroupSyncView

urlpatterns = [
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/sync/", GroupSyncView.as_view(), name="group_sync"),
]
