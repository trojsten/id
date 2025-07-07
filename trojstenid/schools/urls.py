from django.urls.conf import path

from trojstenid.schools.views import (
    SchoolRecordCreateView,
    SchoolRecordListView,
    SchoolSearchView,
)

urlpatterns = [
    path("accounts/school/", SchoolRecordListView.as_view(), name="account_school"),
    path(
        "accounts/school/create/",
        SchoolRecordCreateView.as_view(),
        name="account_school_create",
    ),
    path(
        "accounts/school/search/",
        SchoolSearchView.as_view(),
        name="account_school_search",
    ),
]
