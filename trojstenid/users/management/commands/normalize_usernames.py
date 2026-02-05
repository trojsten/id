import re
import unicodedata

from django.core.management.base import BaseCommand

from trojstenid.users.models import User, UsernameValidator


def normalize_username(username: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", username).encode("ASCII", "ignore").decode()
    )

    if "@" in normalized:
        parts = normalized.split("@", 1)
        if parts[0]:
            normalized = parts[0]
        else:
            normalized = parts[1]

    normalized = re.sub(r"[^\w.-]", "", normalized)

    return normalized


class Command(BaseCommand):
    help = "Validate and normalize usernames"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making changes to the database",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        validator = UsernameValidator()

        users = User.objects.all()

        for user in users:
            try:
                validator(user.username)
            except Exception:
                new_username = normalize_username(user.username)

                if new_username != user.username:
                    self.stdout.write(f"{user.username} ({user.id}) -> {new_username}")

                    if not dry_run:
                        user.username = new_username
                        user.save()
