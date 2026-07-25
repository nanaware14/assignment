from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User


def is_admin(user):
    return bool(user and user.is_authenticated and user.is_admin_role)


def can_view_lead(user, lead):
    if not user.is_authenticated:
        return False
    if user.is_admin_role:
        return True
    return lead.assigned_to_id == user.id


def can_update_status(user, lead):
    return can_view_lead(user, lead)


def can_add_note(user, lead):
    return can_view_lead(user, lead)


def can_assign_lead(user):
    return is_admin(user)


class LeadAPIPermission(BasePermission):
    """
    Public POST supports lead capture. Other operations require authentication.
    Members can only read and update status on assigned leads.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return can_view_lead(request.user, obj)
        if request.method == "DELETE":
            return is_admin(request.user)
        if request.method in {"PUT", "PATCH"}:
            return can_view_lead(request.user, obj)
        return False
