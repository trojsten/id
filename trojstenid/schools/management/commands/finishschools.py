from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from trojstenid.schools.models import UserSchoolRecord


class Command(BaseCommand):
    help = "Automatically end school records that are too long."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("academic_year", type=int)

    def handle(self, *args: Any, **options: Any) -> str | None:
        records = UserSchoolRecord.objects.end_all_expired(options["academic_year"])
        self.stdout.write(self.style.SUCCESS(f"Ended {records} school records."))
