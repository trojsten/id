import json
import logging
from datetime import datetime, timedelta

from allauth.account.models import EmailAddress
from dateutil.parser import isoparse
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.timezone import now
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
]
IAM_DOMAIN = "iam.trojsten.sk"
TFA_ENFORCED_AFTER = timedelta(days=14)


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
    """
    Returns the list of all Google Group in the IAM domain.
    """
    credentials = _get_credentials()
    if credentials is None:
        logger.warning("Google Admin service account not configured")
        return set()

    groups = set()

    directory = build("admin", "directory_v1", credentials=credentials)
    request = directory.groups().list(domain=IAM_DOMAIN)
    while request:
        response = request.execute()

        for group in response.get("groups", []):
            email = group.get("email", "")
            groups.add(email)

        request = directory.groups().list_next(request, response)
    return groups


def fetch_google_group_members(group_email: str) -> set[str]:
    """
    Returns all email addresses of members in a given Google Group.
    """
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


def sync_group(group_email: str) -> None:
    """
    Syncs Google Group membership with ID groups for a single group.

    Users not in the ID group will be added and users that are not in the
    Google Group will be removed.
    """

    members = fetch_google_group_members(group_email)
    user_ids = (
        EmailAddress.objects.filter(email__in=members, verified=True)
        .distinct("user_id")
        .values_list("user_id", flat=True)
    )

    group, _ = Group.objects.get_or_create(name=group_email)
    group.user_set.set(user_ids)  # type:ignore


def sync_iam_groups() -> None:
    """
    Syncs all IAM Google Groups with ID groups.
    """
    for group in fetch_iam_google_groups():
        sync_group(group)


def query_nontfa_users() -> list[tuple[str, datetime, str | None]]:
    """
    Returns all email addresses of users whose account is at least one-week-old and has not enabled 2FA.
    """
    min_account_age = getattr(settings, "GOOGLE_TFA_MIN_ACCOUNT_AGE")
    max_account_age = getattr(settings, "GOOGLE_TFA_MAX_ACCOUNT_AGE")
    if min_account_age is None or max_account_age is None:
        logger.warning("Google TFA account age range not configured")
        return []

    credentials = _get_credentials()
    if credentials is None:
        logger.warning("Google Admin service account not configured")
        return []

    users = []

    directory = build("admin", "directory_v1", credentials=credentials)
    request = directory.users().list(customer="my_customer", orderBy="email")
    while request:
        response = request.execute()

        for user in response.get("users", []):
            email = user.get("primaryEmail", "")
            has_2sv_enabled = user.get("isEnrolledIn2Sv", False)
            has_2sv_enforced = user.get("isEnforcedIn2Sv", False)
            creation_time = (
                isoparse(user["creationTime"]) if "creationTime" in user else None
            )
            if not has_2sv_enabled and has_2sv_enforced and creation_time:
                account_age = now() - creation_time
                if min_account_age <= account_age <= max_account_age:
                    users.append(
                        (
                            email,
                            creation_time + TFA_ENFORCED_AFTER,
                            user.get("secondaryEmail", None),
                        )
                    )

        request = directory.users().list_next(request, response)
    return users
