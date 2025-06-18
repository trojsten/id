from pathlib import PurePath
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import AbstractApplication
from ulid import ULID

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

    from trojstenid.schools.models import UserSchoolRecord


class Application(AbstractApplication):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, blank=True, null=True)


def user_avatar_name(user, filename):
    ext = PurePath(filename).suffix
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
    userschoolrecord_set: "RelatedManager[UserSchoolRecord]"

    @property
    def avatar(self):
        if self.avatar_file:
            return self.avatar_file.url
        return reverse("profile_avatar", kwargs={"user": self.username})

    def get_current_school_record(self) -> "UserSchoolRecord | None":
        now = timezone.now()
        try:
            return (
                self.userschoolrecord_set.filter(start_date__lte=now)
                .filter(Q(end_date__isnull=True) | Q(end_date__gte=now))
                .get()
            )
        except ObjectDoesNotExist:
            return None
