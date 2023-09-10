from django.urls import path

from trojstenid.profiles import views

urlpatterns = [
    path("<user>/avatar/", views.AvatarView.as_view(), name="profile_avatar"),
    path("<user>/", views.ProfileView.as_view(), name="profile"),
]
