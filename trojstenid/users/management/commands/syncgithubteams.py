from typing import Any

from django.core.management.base import BaseCommand

from trojstenid.users.github import sync_github_teams


class Command(BaseCommand):
    help = "Sync GitHub Teams with users from Trojsten ID."

    def handle(self, *args: Any, **options: Any) -> None:
        sync_github_teams()
        self.stdout.write(self.style.SUCCESS("GitHub Teams sync successful."))
