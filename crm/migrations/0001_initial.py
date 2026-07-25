# Generated for the Lead Management System.

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                (
                    "role",
                    models.CharField(
                        choices=[("ADMIN", "Admin"), ("MEMBER", "Member")],
                        default="MEMBER",
                        max_length=20,
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["role"], name="crm_user_role_940f8d_idx"),
                    models.Index(fields=["is_active"], name="crm_user_is_acti_1bb70c_idx"),
                ],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Lead",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=150)),
                ("email", models.EmailField(max_length=254)),
                (
                    "phone",
                    models.CharField(
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Enter a valid phone number.",
                                regex="^[0-9+\\-\\s().]{7,20}$",
                            )
                        ],
                    ),
                ),
                ("company", models.CharField(blank=True, max_length=150)),
                ("source", models.CharField(max_length=100)),
                ("message", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "New"),
                            ("CONTACTED", "Contacted"),
                            ("QUALIFIED", "Qualified"),
                            ("PROPOSAL_SENT", "Proposal Sent"),
                            ("WON", "Won"),
                            ("LOST", "Lost"),
                        ],
                        default="NEW",
                        max_length=30,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[("LOW", "Low"), ("MEDIUM", "Medium"), ("HIGH", "High"), ("URGENT", "Urgent")],
                        default="MEDIUM",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"is_active": True, "role": "MEMBER"},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_leads",
                        to="crm.user",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["status"], name="crm_lead_status_1c6284_idx"),
                    models.Index(fields=["priority"], name="crm_lead_priorit_757108_idx"),
                    models.Index(fields=["source"], name="crm_lead_source_03ef26_idx"),
                    models.Index(fields=["assigned_to", "status"], name="crm_lead_assigne_c21f86_idx"),
                    models.Index(fields=["created_at"], name="crm_lead_created_9a0dcf_idx"),
                    models.Index(fields=["updated_at"], name="crm_lead_updated_edf1a8_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("CREATED", "Created"),
                            ("UPDATED", "Updated"),
                            ("ASSIGNED", "Assigned"),
                            ("STATUS_CHANGED", "Status Changed"),
                            ("NOTE_ADDED", "Note Added"),
                            ("DELETED", "Deleted"),
                        ],
                        max_length=30,
                    ),
                ),
                ("description", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="activity_logs",
                        to="crm.user",
                    ),
                ),
                (
                    "lead",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="activities",
                        to="crm.lead",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["action"], name="crm_activit_action_27094d_idx"),
                    models.Index(fields=["created_at"], name="crm_activit_created_5753a0_idx"),
                    models.Index(fields=["lead", "created_at"], name="crm_activit_lead_id_d0b06b_idx"),
                    models.Index(fields=["actor", "created_at"], name="crm_activit_actor_i_a8752a_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="LeadNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lead_notes",
                        to="crm.user",
                    ),
                ),
                (
                    "lead",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to="crm.lead",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["lead", "created_at"], name="crm_leadnot_lead_id_30f7d5_idx"),
                    models.Index(fields=["author", "created_at"], name="crm_leadnot_author__e6cc7c_idx"),
                ],
            },
        ),
    ]
