"""
Management command to promote an existing employee account to admin,
or create a brand-new admin account directly.

Usage:
    python manage.py promote_admin --email someone@company.com
    python manage.py promote_admin --email admin@company.com --create --password "StrongPass123" --full-name "Canteen Admin"
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

User = get_user_model()


class Command(BaseCommand):
    help = "Promote an existing user to ADMIN role, or create a new admin account."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email address of the admin account.")
        parser.add_argument("--create", action="store_true", help="Create the account if it does not exist.")
        parser.add_argument("--password", required=False, help="Password (required when using --create).")
        parser.add_argument("--full-name", required=False, default="Admin User", help="Full name (used with --create).")

    def handle(self, *args, **options):
        email = options["email"].strip().lower()
        user = User.objects.filter(email=email).first()

        if user is None:
            if not options["create"]:
                raise CommandError(
                    f"No user found with email '{email}'. Use --create to make a new admin account."
                )
            if not options["password"]:
                raise CommandError("--password is required when using --create.")
            try:
                user = User.objects.create_superuser(
                    email=email,
                    password=options["password"],
                    full_name=options["full_name"],
                )
            except IntegrityError as exc:
                raise CommandError(f"Could not create user: {exc}")
            self.stdout.write(self.style.SUCCESS(f"Created new admin account: {user.email}"))
            return

        user.role = User.Role.ADMIN
        user.is_staff = True
        user.save(update_fields=["role", "is_staff"])
        self.stdout.write(self.style.SUCCESS(f"Promoted '{user.email}' to ADMIN role."))
