import logging

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed, user_logged_out
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.signals import (
    user_logged_out as dj_user_logged_out,
)
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from oauth2_provider.signals import app_authorized

from trojstenid import audit
from trojstenid.users.models import User
from trojstenid.users.tasks import queue_user_update, sync_github_teams_for_user, sync_groups

logger = logging.getLogger(__name__)


@receiver(email_confirmed)
def sync_groups_after_confirm(request, email_address: EmailAddress, **kwargs):
    if email_address.email.endswith("@trojsten.sk"):
        logger.info(
            f"user {email_address.user.username} has verified @trojsten.sk address, syncing groups"
        )
        sync_groups.delay()


@receiver([user_logged_out, dj_user_logged_out])
def log_user_logout(request, user: User, **kwargs):
    audit.log(request, "logged out")


@receiver(app_authorized)
def log_app_authorization(sender, request, token, **kwargs):
    logger.info(
        f"application {token.application.name} was authorized for "
        f"user {token.user.username}",
    )


@receiver(post_save, sender=User)
def user_saved(sender, instance: User, *, update_fields, **kwargs):
    if update_fields is not None and update_fields.issubset({"last_login"}):
        return
    queue_user_update(instance.id)


@receiver(post_save, sender=EmailAddress)
def emailaddress_saved(sender, instance: EmailAddress, **kwargs):
    queue_user_update(instance.user_id)  # type:ignore


@receiver(m2m_changed, sender=User.groups.through)
def groups_changed(sender, instance, **kwargs):
    if not isinstance(instance, User):
        return
    queue_user_update(instance.id)


@receiver(post_save, sender=SocialAccount)
def socialaccount_saved(sender, instance: SocialAccount, **kwargs):
    logger.info(
        f"socialaccount saved for user {instance.user.username} (provider {instance.provider})"
    )

    if instance.provider == "github":
        sync_github_teams_for_user.delay(instance.user_id)  # type: ignore
