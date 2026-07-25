from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import ActivityLog, Lead, LeadNote, User


class CRMTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="pass12345",
            role=User.Role.ADMIN,
        )
        self.member = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="pass12345",
            role=User.Role.MEMBER,
        )
        self.other_member = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass12345",
            role=User.Role.MEMBER,
        )
        self.lead = Lead.objects.create(
            full_name="Ava Smith",
            email="ava@example.com",
            phone="+1 555 0101",
            company="Acme",
            source="Website",
            assigned_to=self.member,
        )


class AuthenticationTests(CRMTestCase):
    def test_login_required_for_dashboard(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_user_can_login(self):
        response = self.client.post(
            reverse("login"),
            {"username": "member", "password": "pass12345"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Member Dashboard")


class RolePermissionTests(CRMTestCase):
    def test_admin_can_view_all_leads(self):
        Lead.objects.create(
            full_name="Ben Taylor",
            email="ben@example.com",
            phone="+1 555 0202",
            company="Beta",
            source="Referral",
            assigned_to=self.other_member,
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse("lead_list"))
        self.assertContains(response, "Ava Smith")
        self.assertContains(response, "Ben Taylor")

    def test_member_only_sees_assigned_leads(self):
        Lead.objects.create(
            full_name="Ben Taylor",
            email="ben@example.com",
            phone="+1 555 0202",
            company="Beta",
            source="Referral",
            assigned_to=self.other_member,
        )
        self.client.force_login(self.member)
        response = self.client.get(reverse("lead_list"))
        self.assertContains(response, "Ava Smith")
        self.assertNotContains(response, "Ben Taylor")

    def test_member_cannot_delete_lead(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse("lead_delete", args=[self.lead.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Lead.objects.filter(pk=self.lead.pk).exists())

    def test_admin_can_delete_lead(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("lead_delete", args=[self.lead.pk]), follow=True)
        self.assertRedirects(response, reverse("lead_list"))
        self.assertFalse(Lead.objects.filter(pk=self.lead.pk).exists())
        self.assertTrue(
            ActivityLog.objects.filter(
                actor=self.admin,
                action=ActivityLog.Action.DELETED,
                description__icontains=self.lead.full_name,
            ).exists()
        )

    def test_member_cannot_assign_lead(self):
        self.client.force_login(self.member)
        response = self.client.post(
            reverse("lead_assign", args=[self.lead.pk]),
            {"assigned_to": self.other_member.pk},
        )
        self.assertEqual(response.status_code, 403)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.assigned_to, self.member)


class LeadWorkflowTests(CRMTestCase):
    def test_public_lead_creation(self):
        response = self.client.post(
            reverse("lead_capture"),
            {
                "full_name": "Chris Lee",
                "email": "chris@example.com",
                "phone": "+1 555 0303",
                "company": "Cobalt",
                "source": "LinkedIn",
                "message": "Interested in services.",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Lead.objects.filter(email="chris@example.com").exists())
        self.assertTrue(ActivityLog.objects.filter(action=ActivityLog.Action.CREATED).exists())

    def test_admin_can_assign_lead(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("lead_assign", args=[self.lead.pk]),
            {"assigned_to": self.other_member.pk},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.assigned_to, self.other_member)
        self.assertTrue(ActivityLog.objects.filter(action=ActivityLog.Action.ASSIGNED).exists())

    def test_member_can_update_assigned_lead_status(self):
        self.client.force_login(self.member)
        response = self.client.post(
            reverse("lead_status_update", args=[self.lead.pk]),
            {"status": Lead.Status.CONTACTED},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.CONTACTED)

    def test_member_can_add_note_to_assigned_lead(self):
        self.client.force_login(self.member)
        response = self.client.post(
            reverse("lead_note_create", args=[self.lead.pk]),
            {"body": "Called and left voicemail."},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(LeadNote.objects.filter(lead=self.lead, author=self.member).exists())


class LeadAPITests(CRMTestCase):
    def setUp(self):
        super().setUp()
        self.api = APIClient()

    def test_api_public_post_creates_lead(self):
        response = self.api.post(
            reverse("api_lead_list"),
            {
                "full_name": "Dana Park",
                "email": "dana@example.com",
                "phone": "+1 555 0404",
                "company": "Delta",
                "source": "Webinar",
                "message": "Please contact me.",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lead.objects.filter(email="dana@example.com").exists())

    def test_api_member_cannot_delete(self):
        self.api.force_authenticate(self.member)
        response = self.api.delete(reverse("api_lead_detail", args=[self.lead.pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_member_can_update_status_only(self):
        self.api.force_authenticate(self.member)
        response = self.api.put(
            reverse("api_lead_detail", args=[self.lead.pk]),
            {"status": Lead.Status.QUALIFIED},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.status, Lead.Status.QUALIFIED)

    def test_api_member_cannot_update_unassigned_lead(self):
        other_lead = Lead.objects.create(
            full_name="Eli Ray",
            email="eli@example.com",
            phone="+1 555 0505",
            company="Echo",
            source="Partner",
            assigned_to=self.other_member,
        )
        self.api.force_authenticate(self.member)
        response = self.api.get(reverse("api_lead_detail", args=[other_lead.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
