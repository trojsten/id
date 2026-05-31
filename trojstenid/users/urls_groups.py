from django.urls import path

from trojstenid.users.views import GroupListView, GroupSyncView

urlpatterns = [
    path("", GroupListView.as_view(), name="group_list"),
    path("sync/", GroupSyncView.as_view(), name="group_sync"),
]
