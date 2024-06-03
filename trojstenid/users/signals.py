from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed, user_logged_in
from django.contrib.auth.models import Group
from django.dispatch import receiver

from trojstenid.users.models import User


@receiver(user_logged_in)
def assign_groups_after_login(request, user: User, **kwargs):
    has_trojsten_mail = EmailAddress.objects.filter(
        user=user, email__endswith="@trojsten.sk", verified=True
    ).exists()
    if has_trojsten_mail:
        veduci, _ = Group.objects.get_or_create(name="trojsten:veduci")
        user.groups.add(veduci)


@receiver(email_confirmed)
def assign_groups_after_confirm(request, email: EmailAddress, **kwargs):
    if email.email.endswith("@trojsten.sk"):
        veduci, _ = Group.objects.get_or_create(name="trojsten:veduci")
        email.user.groups.add(veduci)
