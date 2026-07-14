import logging

import requests
from django.db import transaction
from django_rq import job

from trojstenid.users.github import sync_github_teams
from trojstenid.users.google_groups import sync_iam_groups
from trojstenid.users.models import Application, User
from trojstenid.users.serializers import UserSerializer

logger = logging.getLogger(__name__)


def queue_user_update(user_id: int):
    transaction.on_commit(lambda: send_user_update.delay(user_id))


@job
def send_user_update(user_id: int):
    logger.info(f"pushing user update (uid {user_id})")
    user = User.objects.get(id=user_id)
    user_json = UserSerializer(user).data

    applications = Application.objects.exclude(push_urls="")
    for app in applications:
        urls = app.push_urls.split()
        for url in urls:
            try:
                requests.post(
                    url,
                    json=user_json,
                    timeout=15,
                    headers={
                        "X-Client-ID": app.client_id,
                        "X-Client-Secret": app.client_secret,
                    },
                )
            except Exception as e:
                # No special error handling, as we treat this channel as "best-effort".
                # Apps can always request fresh data through API or OIDC flow.
                logger.error(f"error while pushing user update to {url}: {e}")


@job
def sync_groups():
    sync_iam_groups()

    sync_github_teams()


@job
def sync_github_teams_for_user(user_id: int | None = None):
    logger.info(f"syncing GitHub teams for user_id={user_id}")

    qs = User.objects.all()
    if user_id is not None:
        qs = qs.filter(id=user_id)

    sync_github_teams(qs)
