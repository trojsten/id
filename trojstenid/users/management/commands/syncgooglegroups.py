from typing import Any

from django.core.management.base import BaseCommand

from trojstenid.users.google_groups import sync_iam_groups


class Command(BaseCommand):
    help = "Sync Google Groups from the IAM domain with Django auth groups."

    def handle(self, *args: Any, **options: Any) -> None:
        sync_iam_groups()
        self.stdout.write(self.style.SUCCESS("Google Groups sync successful."))
