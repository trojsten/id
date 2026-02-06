import logging

import requests
from django_rq import job

from trojstenid.users.models import Application, User
from trojstenid.users.serializers import UserSerializer

logger = logging.getLogger(__name__)


@job
def send_user_update(user_id: int):
    """
    Send user updates to all registered push URLs.

    Each URL receives a POST request with serialized user data. Applications should:
    - Validate X-Client-ID and X-Client-Secret with their stored values.
    - Update existing user data if they have information about this user
    - Ignore requests for unknown users (do not create new ones)
    - Handle now_known_as transitions:
      * Unknown now_known_as: update original user's OIDC uid
      * Known now_known_as: merge original user into the now_known_as user
    """
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
