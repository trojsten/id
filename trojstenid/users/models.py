from os import path

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.urls import reverse
from oauth2_provider.models import AbstractApplication
from ulid import ULID


class Application(AbstractApplication):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, blank=True, null=True)

    def is_usable(self, request):
        if self.group is not None:
            return request.user.groups.contains(self.group)
        return True


def user_avatar_name(user, filename):
    _, ext = path.splitext(filename)
    return f"avatars/{ULID()}{ext}"


class ImageField(models.ImageField):
    """
    A custom ImageField that can be serialized by AllAuth during signup.
    """

    def from_db_value(self, *args):
        return ""

    def get_db_converters(self, connection):
        return []


class User(AbstractUser):
    avatar_file = ImageField(upload_to=user_avatar_name, blank=True)

    @property
    def avatar(self):
        if self.avatar_file:
            return self.avatar_file.url
        return reverse("profile_avatar", kwargs={"user": self.username})
