from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from trojstenid.users.google_api import query_nontfa_users


class Command(BaseCommand):
    help = "Send mail alerts to Google users without TFA enabled"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without actually sending emails",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        nontfa_users = query_nontfa_users()

        if not nontfa_users:
            self.stdout.write(self.style.NOTICE("No users found without 2FA enabled."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING(f"Found {len(nontfa_users)} user(s) requiring 2FA alert.\n"))

        sent_count = 0
        failed_count = 0

        for email, required_after in nontfa_users:
            if dry_run:
                self.stdout.write(
                    self.style.NOTICE(f"[DRY-RUN] Would alert {email:<32} | 2FA required after: {required_after}")
                )
                continue

            try:
                content = render_to_string(
                    "account/email/tfa_alert.html",
                    {"email": email, "required_after": required_after},
                )

                send_mail(
                    subject="Dvojstupňové overenie tvojho Trojsten Google účtu",
                    message=content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Sent to '{email}', 2FA required after: {required_after}")
                )
            except Exception as e:
                failed_count += 1
                self.stderr.write(
                    self.style.ERROR(f"Failed to send to '{email}', Error: {e}")
                )


        self.stdout.write("")
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Dry run complete."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Completed. Sent: {sent_count}, failed: {failed_count}"
                )
            )