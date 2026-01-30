import logging

import requests
from django_rq import job

from trojstenid.users.models import Application, User
from trojstenid.users.serializers import UserSerializer

logger = logging.getLogger(__name__)


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
