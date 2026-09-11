from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
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

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Found {len(nontfa_users)} user(s) requiring 2FA alert.\n"
            )
        )

        if dry_run:
            for email, required_after, _ in nontfa_users:
                self.stdout.write(
                    self.style.NOTICE(
                        f"[DRY-RUN] Would alert {email}, 2FA required after: {required_after}"
                    )
                )
            self.stdout.write(self.style.SUCCESS("\nDry run complete."))
            return

        sent_count = 0
        failed_count = 0

        connection = get_connection()
        try:
            connection.open()

            for email, required_after, secondary_email in nontfa_users:
                try:
                    content = render_to_string(
                        "account/email/tfa_alert.txt",
                        {"email": email, "required_after": required_after},
                    )

                    msg = EmailMultiAlternatives(
                        subject="Dvojstupňové overenie tvojho Trojsten Google účtu",
                        body=content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                        cc=secondary_email if secondary_email else None,
                        connection=connection,
                    )
                    msg.send()

                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sent to '{email}', 2FA required after: {required_after}"
                        )
                    )
                except Exception as e:
                    failed_count += 1
                    self.stderr.write(
                        self.style.ERROR(f"Failed to send to '{email}', Error: {e}")
                    )

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during email delivery: {e}"))
        finally:
            connection.close()

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted. Sent: {sent_count}, failed: {failed_count}"
            )
        )
