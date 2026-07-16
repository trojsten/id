import re
import secrets
from datetime import date
from pathlib import PurePath
from typing import TYPE_CHECKING

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser, Group
from django.core import validators
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from oauth2_provider.models import AbstractApplication
from ulid import ULID

if TYPE_CHECKING:
    from allauth.account.models import EmailAddress
    from django.db.models.manager import RelatedManager

    from trojstenid.schools.models import UserSchoolRecord


class Application(AbstractApplication):
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, blank=True, null=True)
    push_urls = models.TextField(blank=True)


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


@deconstructible()
class UsernameValidator(validators.RegexValidator):
    regex = r"^[\w.-]+\Z"
    message = "Používateľské meno môže obsahovať len písmená, čísla a znaky ./-/_"
    flags = re.ASCII


username_validators = [UsernameValidator()]
WIFI_PASSWORD_ALPHABET = "346789ABCDEFGHJKLMNPQRTUVWXY"  # noqa: S105
WIFI_PASSWORD_LENGTH = 12


class WifiPassword(models.Model):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, blank=True, null=True
    )
    username = models.CharField(
        max_length=150, unique=True, validators=username_validators
    )
    password = models.CharField(max_length=128)
    allowed_callers = models.TextField(blank=True)

    def __str__(self):
        return self.username

    def set_password(self, raw_password=None):
        if raw_password is None:
            raw_password = "".join(
                secrets.choice(WIFI_PASSWORD_ALPHABET)
                for _ in range(WIFI_PASSWORD_LENGTH)
            )
        self.password = make_password(raw_password)
        return raw_password

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def allows_caller(self, calling_station_id):
        callers = [
            c.strip().upper() for c in self.allowed_callers.split(",") if c.strip()
        ]
        if not callers:
            return True
        caller = calling_station_id.strip().upper()
        normalized_caller = caller.replace(":", "").replace("-", "")
        return any(
            caller == allowed
            or normalized_caller == allowed.replace(":", "").replace("-", "")
            for allowed in callers
        )


class User(AbstractUser):
    id: int

    avatar_file = ImageField(upload_to=user_avatar_name, blank=True)
    now_known_as = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="previously_known_as",
    )
    now_known_as_id: int

    previously_known_as: "RelatedManager[User]"
    userschoolrecord_set: "RelatedManager[UserSchoolRecord]"
    emailaddress_set: "RelatedManager[EmailAddress]"

    @property
    def avatar(self):
        if self.avatar_file:
            return self.avatar_file.url
        return reverse("profile_avatar", kwargs={"user": self.username})

    def get_current_school_record(
        self, at: date | None = None
    ) -> "UserSchoolRecord | None":
        if at is None:
            at = timezone.now()
        try:
            return (
                self.userschoolrecord_set.filter(start_date__lte=at)
                .filter(Q(end_date__isnull=True) | Q(end_date__gte=at))
                .select_related("school", "school_type")
                .get()
            )
        except ObjectDoesNotExist:
            return None
