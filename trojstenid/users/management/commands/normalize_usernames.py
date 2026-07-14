import re
import unicodedata

from django.core.management.base import BaseCommand
from django.db import transaction

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

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        validator = UsernameValidator()

        users = User.objects.all()

        for user in users:
            try:
                validator(user.username)
            except Exception:
                new_username = normalize_username(user.username)

                if new_username == user.username:
                    continue

                # Check if normalized username becomes empty
                if not new_username:
                    new_username = self.prompt_for_username(
                        user,
                        reason="Normalized username would be empty",
                    )

                # Check for duplicates
                duplicate_user = (
                    User.objects.filter(username=new_username)
                    .exclude(id=user.id)
                    .first()
                )
                if duplicate_user:
                    new_username = self.prompt_for_username(
                        user,
                        reason=f"Username '{new_username}' already exists (user ID: {duplicate_user.id})",
                    )

                self.stdout.write(f"{user.username} ({user.id}) -> {new_username}")

                if not dry_run:
                    user.username = new_username
                    user.save()

    def prompt_for_username(self, user: User, reason: str) -> str:
        """Prompt the user for a new username."""
        self.stdout.write(self.style.WARNING(f"\n{reason}"))
        self.stdout.write(f"Old username: {user.username}")
        self.stdout.write(f"Email: {user.email}")
        self.stdout.write(f"Full name: {user.get_full_name() or '(not set)'}")

        while True:
            new_username = input("Enter new username: ").strip()

            if not new_username:
                self.stdout.write(self.style.ERROR("Username cannot be empty."))
                continue

            # Validate the username format
            validator = UsernameValidator()
            try:
                validator(new_username)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Invalid username: {e}"))
                continue

            # Check for duplicates
            duplicate_user = (
                User.objects.filter(username=new_username).exclude(id=user.id).first()
            )
            if duplicate_user:
                self.stdout.write(
                    self.style.ERROR(
                        f"Username '{new_username}' already in use by user ID {duplicate_user.id}"
                    )
                )
                continue

            return new_username
