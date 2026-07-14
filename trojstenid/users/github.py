import logging
from collections import defaultdict

from django.conf import settings
from github import Auth, Github, GithubIntegration
from github.Team import Team

from trojstenid.users.models import User

logger = logging.getLogger(__name__)


def _get_github() -> Github:
    auth = Auth.AppAuth(settings.GITHUB_APP_ID, settings.GITHUB_APP_PRIVATE_KEY)
    gi = GithubIntegration(auth=auth)

    installation = gi.get_org_installation(settings.GITHUB_ORG_NAME)

    token = gi.get_access_token(installation.id)

    return Github(token.token)


def get_teams_for_user(user: User, teams_mapping: dict[str, Team]) -> list[Team]:
    teams = []
    for group in user.groups.all():
        team_name = settings.GITHUB_TEAMS.get(group.name)
        if team_name:
            teams.append(teams_mapping[team_name])
    return teams


def sync_github_teams(qs=None):
    if not settings.GITHUB_TEAMS:
        return
    if (
        settings.GITHUB_APP_ID <= 0
        or not settings.GITHUB_APP_PRIVATE_KEY
        or not settings.GITHUB_ORG_NAME
    ):
        logger.warning("GitHub Teams sync not configured")
        return
    if qs is None:
        qs = User.objects.all()

    users = (
        qs.filter(
            socialaccount__provider="github",
            groups__name__in=settings.GITHUB_TEAMS.keys(),
        )
        .prefetch_related("socialaccount_set", "groups")
        .distinct()
    )

    if not users.exists():
        return

    logger.info(
        f"Syncing {users.count()} users with GitHub teams in organization {settings.GITHUB_ORG_NAME}"
    )

    github = _get_github()
    org = github.get_organization(settings.GITHUB_ORG_NAME)

    teams_mapping = {
        team: org.get_team_by_slug(team) for team in settings.GITHUB_TEAMS.values()
    }

    new_team_membership = defaultdict(lambda: [])

    org_members = set(org.get_members())

    for user in users:
        socialaccount_github = user.socialaccount_set.get(provider="github")

        github_user = github.get_user_by_id(int(socialaccount_github.uid))

        teams = get_teams_for_user(user, teams_mapping)

        if not teams:
            continue

        if github_user not in org_members:
            org.invite_user(user=github_user, role="direct_member", teams=teams)
            logger.info(
                f"Invited user {user.username} to GitHub teams {', '.join([team.name for team in teams])} in organization {settings.GITHUB_ORG_NAME}"
            )
            continue

        for team in teams:
            new_team_membership[team].append(github_user)

    for team, members in new_team_membership.items():
        current_members = list(team.get_members())
        current_member_ids = {member.id for member in current_members}

        for member in members:
            if member.id not in current_member_ids:
                team.add_membership(member)
                logger.info(
                    f"Added user {member.login} to GitHub team {team.name} in organization {settings.GITHUB_ORG_NAME}"
                )
