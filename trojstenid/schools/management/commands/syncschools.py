from typing import Any

from django.core.management.base import BaseCommand

from trojstenid.schools.services.school_sync import sync_schools


class Command(BaseCommand):
    help = "Sync school database."

    def handle(self, *args: Any, **options: Any) -> str | None:
        sync_schools()
        self.stdout.write(self.style.SUCCESS("School sync sucessfull."))
