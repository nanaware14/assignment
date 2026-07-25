from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ActivityLog, Lead, LeadNote, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("CRM", {"fields": ("role",)}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("CRM", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")


class LeadNoteInline(admin.TabularInline):
    model = LeadNote
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "company", "status", "priority", "assigned_to", "created_at")
    list_filter = ("status", "priority", "source", "assigned_to")
    search_fields = ("full_name", "email", "phone", "company", "source")
    date_hierarchy = "created_at"
    inlines = [LeadNoteInline]


@admin.register(LeadNote)
class LeadNoteAdmin(admin.ModelAdmin):
    list_display = ("lead", "author", "created_at")
    search_fields = ("lead__full_name", "author__username", "body")
    list_filter = ("created_at",)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "lead", "actor", "description", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("description", "lead__full_name", "actor__username")
    readonly_fields = ("lead", "actor", "action", "description", "created_at")
