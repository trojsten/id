import logging
from operator import attrgetter

from allauth.account.models import EmailAddress
from django.db import transaction
from django.db.models import ForeignObjectRel, Model

from trojstenid.badges.models import BadgeAssignment
from trojstenid.users.models import User

logger = logging.getLogger(__name__)


FIELDS_TO_MERGE_MANUALLY = [
    "emailaddress",  # unique on (user_id, primary)
    # The following always contain both, one (with +) is the "through" model.
    "User_groups+",  # unique on (user_id, group_id)
    "groups",
    "User_user_permissions+",  # unique on (user_id, permission_id)
    "user_permissions",
    #
    "badgeassignment",  # unique on (user, badge)
    # we don't want to mess with oauth tokens, they'll expire
    "oauth2_provider_grant",
    "oauth2_provider_accesstoken",
    "oauth2_provider_refreshtoken",
    "oauth2_provider_idtoken",
]


@transaction.atomic
def merge_user_into(user: User, into: User):
    """
    Merge user `user` into user `into`.

    All attributes of `user` not present on `into` will be copied over.
    All related objects of `user` will be reassigned to `into`.

    User `user` will get deactivated.

    The old `user` should be considered destroyed and never to be touched again.
    It may or may not contain data, or the data contained within can be incomplete.
    """
    if user.id == into.id:
        return

    logger.info(f"Merging user {user.id} -> {into.id}.")

    fields = user._meta.get_fields(include_hidden=True)
    field_names = list(map(attrgetter("name"), fields))
    logger.debug(f"Found {len(fields)} fields: {field_names}")

    save_into = False
    for field in fields:
        if field.name in FIELDS_TO_MERGE_MANUALLY:
            logger.info(f"Skipping field {field.name}.")
            continue

        if isinstance(field, ForeignObjectRel):
            model: type[Model] = field.related_model  # type:ignore
            remote_field = field.remote_field.name

            instances = model.objects.filter(**{remote_field: user})
            logger.info(
                f"{field.name}: changing {remote_field} on {model._meta.label} instances: {instances.count()}"
            )

            instances.update(**{remote_field: into})
        elif not field.primary_key:  # type:ignore
            value_user = getattr(user, field.name)
            value_into = getattr(into, field.name)

            if value_user and not value_into:
                logger.info(
                    f"User {into.id} has empty {field.name}, setting to {user.id}'s value."
                )
                setattr(into, field.name, value_user)
                save_into = True

    merge_others(user, into)

    logger.info(f"Saving merged user {user.id}.")
    user.is_active = False
    user.now_known_as = into
    user.save()

    if save_into:
        into.save()

    logger.info(f"Merge {user.id} -> {into.id} completed.")


def merge_others(user: User, into: User):
    EmailAddress.objects.filter(user=user).update(user=into, primary=False)
    into.groups.add(*user.groups.all())
    into.user_permissions.add(*user.user_permissions.all())

    user_badges = set(
        BadgeAssignment.objects.filter(user=user).values_list("badge_id", flat=True)
    )
    into_badges = set(
        BadgeAssignment.objects.filter(user=into).values_list("badge_id", flat=True)
    )

    missing_badges = user_badges - into_badges
    BadgeAssignment.objects.filter(user=user, badge_id__in=missing_badges).update(
        user=into
    )
