import logging

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed, user_logged_in, user_logged_out
from django.contrib.auth.models import Group
from django.contrib.auth.signals import (
    user_logged_in as dj_user_logged_in,
)
from django.contrib.auth.signals import (
    user_logged_out as dj_user_logged_out,
)
from django.dispatch import receiver
from oauth2_provider.signals import app_authorized

from trojstenid import audit
from trojstenid.users.models import User

logger = logging.getLogger(__name__)


@receiver([user_logged_in, dj_user_logged_in])
def assign_groups_after_login(request, user: User, **kwargs):
    audit.log(request, "logged in")

    has_trojsten_mail = EmailAddress.objects.filter(
        user=user, email__endswith="@trojsten.sk", verified=True
    ).exists()
    if has_trojsten_mail:
        logger.info(
            f"user {user.username} has @trojsten.sk address, adding "
            "trojsten:veduci group on login"
        )
        veduci, _ = Group.objects.get_or_create(name="trojsten:veduci")
        user.groups.add(veduci)


@receiver(email_confirmed)
def assign_groups_after_confirm(request, email_address: EmailAddress, **kwargs):
    if email_address.email.endswith("@trojsten.sk"):
        logger.info(
            f"user {email_address.user.username} has @trojsten.sk address, adding "
            "trojsten:veduci group on verification"
        )
        veduci, _ = Group.objects.get_or_create(name="trojsten:veduci")
        email_address.user.groups.add(veduci)


@receiver([user_logged_out, dj_user_logged_out])
def log_user_logout(request, user: User, **kwargs):
    audit.log(request, "logged out")


@receiver(app_authorized)
def log_app_authorization(sender, request, token, **kwargs):
    logger.info(
        f"application {token.application.name} was authorized for "
        f"user {token.user.username}",
    )
