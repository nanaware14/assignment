from django.core.management.base import BaseCommand

from crm.models import Lead, User


class Command(BaseCommand):
    help = "Create sample admin, member, and lead records for local review."

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "role": User.Role.ADMIN,
                "is_staff": True,
            },
        )
        admin.set_password("Admin@12345")
        admin.role = User.Role.ADMIN
        admin.is_staff = True
        admin.save()

        member, _ = User.objects.get_or_create(
            username="member",
            defaults={
                "email": "member@example.com",
                "first_name": "Member",
                "last_name": "User",
                "role": User.Role.MEMBER,
            },
        )
        member.set_password("Member@12345")
        member.role = User.Role.MEMBER
        member.save()

        Lead.objects.get_or_create(
            email="lead@example.com",
            defaults={
                "full_name": "Sample Lead",
                "phone": "+1 555 0199",
                "company": "Digital Heroes",
                "source": "Website",
                "message": "Looking for CRM support.",
                "assigned_to": member,
                "priority": Lead.Priority.HIGH,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
