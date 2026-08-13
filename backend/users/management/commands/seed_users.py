from django.core.management.base import BaseCommand

from users.models import User
from django.conf import settings

from django.core.management.base import BaseCommand, CommandError

def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_users is development-only.")


class Command(BaseCommand):
    help = "Create default users for development"

    USERS = [
        {
            "email": "admin@aurahr.com",
            "first_name": "System",
            "last_name": "Admin",
            "role": User.Roles.ADMIN,
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "email": "hr@aurahr.com",
            "first_name": "HR",
            "last_name": "Manager",
            "role": User.Roles.HR,
        },
        {
            "email": "manager@aurahr.com",
            "first_name": "Project",
            "last_name": "Manager",
            "role": User.Roles.MANAGER,
        },
        {
            "email": "employee@aurahr.com",
            "first_name": "John",
            "last_name": "Employee",
            "role": User.Roles.EMPLOYEE,
        },
    ]

    PASSWORD = "Password@123"

    def handle(self, *args, **options):
        for data in self.USERS:

            email = data["email"]

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    **data,
                    "is_verified": True,
                    "is_active": True,
                },
            )

            # Always ensure password is hashed
            user.set_password(self.PASSWORD)

            # Keep these values updated even if the user already exists
            user.role = data["role"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.is_verified = True
            user.is_active = True
            user.is_staff = data.get("is_staff", False)
            user.is_superuser = data.get("is_superuser", False)

            user.save()

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {email}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Updated: {email}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "\nSeed completed successfully."
            )
        )