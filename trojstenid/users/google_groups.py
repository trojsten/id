import json
import logging

from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/admin.directory.group.readonly"]
GROUP_DOMAIN = "iam.trojsten.sk"


def _get_credentials():
    sa_config = getattr(settings, "GOOGLE_ADMIN_SERVICE_ACCOUNT", "")
    subject = getattr(settings, "GOOGLE_ADMIN_SUBJECT", "")

    if not sa_config or not subject:
        return None

    info = json.loads(sa_config)

    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=SCOPES, subject=subject
    )
    return credentials


def fetch_iam_google_groups() -> set[str]:
    credentials = _get_credentials()
    if credentials is None:
        logger.warning("Google Admin service account not configured")
        return set()

    groups = set()

    directory = build("admin", "directory_v1", credentials=credentials)
    request = directory.groups().list(domain=GROUP_DOMAIN)
    while request:
        response = request.execute()

        for group in response.get("groups", []):
            email = group.get("email", "")
            groups.add(email)

        request = directory.groups().list_next(request, response)
    return groups


def fetch_google_group_members(group_email: str) -> set[str]:
    credentials = _get_credentials()
    if credentials is None:
        logger.warning("Google Admin service account not configured")
        return set()

    members = set()

    directory = build("admin", "directory_v1", credentials=credentials)
    request = directory.members().list(
        groupKey=group_email, includeDerivedMembership=True
    )
    while request:
        response = request.execute()

        for member in response.get("members", []):
            email = member.get("email", "")
            members.add(email)

        request = directory.members().list_next(request, response)
    return members
