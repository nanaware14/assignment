from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    CRMUserCreationForm,
    CRMUserUpdateForm,
    LeadAssignForm,
    LeadCaptureForm,
    LeadForm,
    LeadNoteForm,
    LeadStatusForm,
)
from .models import ActivityLog, Lead, User
from .permissions import can_add_note, can_assign_lead, can_update_status, can_view_lead, is_admin


def log_activity(lead, actor, action, description):
    ActivityLog.objects.create(
        lead=lead,
        actor=actor if actor and actor.is_authenticated else None,
        action=action,
        description=description,
    )


def get_visible_leads(user):
    queryset = Lead.objects.select_related("assigned_to")
    if user.is_admin_role:
        return queryset
    return queryset.filter(assigned_to=user)


def admin_required(user):
    if not is_admin(user):
        raise PermissionDenied("You do not have permission to access this page.")


def paginate(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def lead_capture(request):
    if request.method == "POST":
        form = LeadCaptureForm(request.POST)
        if form.is_valid():
            lead = form.save()
            log_activity(
                lead=lead,
                actor=request.user,
                action=ActivityLog.Action.CREATED,
                description=f"Lead {lead.full_name} submitted the public capture form.",
            )
            messages.success(request, "Thanks. Your information has been submitted.")
            return redirect("lead_capture")
    else:
        form = LeadCaptureForm()
    return render(request, "crm/lead_capture.html", {"form": form})


@login_required
def dashboard(request):
    if request.user.is_admin_role:
        context = {
            "total_leads": Lead.objects.count(),
            "new_leads": Lead.objects.filter(status=Lead.Status.NEW).count(),
            "won_leads": Lead.objects.filter(status=Lead.Status.WON).count(),
            "lost_leads": Lead.objects.filter(status=Lead.Status.LOST).count(),
            "recent_activities": ActivityLog.objects.select_related("lead", "actor")[:8],
        }
        return render(request, "crm/dashboard_admin.html", context)

    assigned = Lead.objects.filter(assigned_to=request.user)
    context = {
        "assigned_leads": assigned.count(),
        "pending_leads": assigned.exclude(status__in=[Lead.Status.WON, Lead.Status.LOST]).count(),
        "completed_leads": assigned.filter(status__in=[Lead.Status.WON, Lead.Status.LOST]).count(),
        "recent_leads": assigned[:8],
    }
    return render(request, "crm/dashboard_member.html", context)


@login_required
def lead_list(request):
    leads = get_visible_leads(request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    priority = request.GET.get("priority", "").strip()
    source = request.GET.get("source", "").strip()
    ordering = request.GET.get("ordering", "-created_at")

    if query:
        leads = leads.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(company__icontains=query)
            | Q(source__icontains=query)
        )
    if status:
        leads = leads.filter(status=status)
    if priority:
        leads = leads.filter(priority=priority)
    if source:
        leads = leads.filter(source__icontains=source)

    allowed_ordering = {
        "created_at",
        "-created_at",
        "updated_at",
        "-updated_at",
        "full_name",
        "-full_name",
        "status",
        "-status",
        "priority",
        "-priority",
    }
    leads = leads.order_by(ordering if ordering in allowed_ordering else "-created_at")

    context = {
        "page_obj": paginate(request, leads),
        "query": query,
        "selected_status": status,
        "selected_priority": priority,
        "source": source,
        "ordering": ordering,
        "status_choices": Lead.Status.choices,
        "priority_choices": Lead.Priority.choices,
    }
    return render(request, "crm/lead_list.html", context)


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead.objects.select_related("assigned_to"), pk=pk)
    if not can_view_lead(request.user, lead):
        raise PermissionDenied
    context = {
        "lead": lead,
        "note_form": LeadNoteForm(),
        "status_form": LeadStatusForm(instance=lead),
        "assign_form": LeadAssignForm(instance=lead) if can_assign_lead(request.user) else None,
    }
    return render(request, "crm/lead_detail.html", context)


@login_required
def lead_create(request):
    admin_required(request.user)
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save()
            log_activity(lead, request.user, ActivityLog.Action.CREATED, f"Lead {lead.full_name} was created.")
            messages.success(request, "Lead created successfully.")
            return redirect(lead)
    else:
        form = LeadForm()
    return render(request, "crm/lead_form.html", {"form": form, "title": "Create Lead"})


@login_required
def lead_update(request, pk):
    admin_required(request.user)
    lead = get_object_or_404(Lead, pk=pk)
    previous_status = lead.status
    previous_assignee_id = lead.assigned_to_id
    if request.method == "POST":
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            lead = form.save()
            if previous_assignee_id != lead.assigned_to_id:
                action = ActivityLog.Action.ASSIGNED
                description = f"Lead assigned to {lead.assigned_to or 'nobody'}."
            elif previous_status != lead.status:
                action = ActivityLog.Action.STATUS_CHANGED
                description = f"Status changed to {lead.get_status_display()}."
            else:
                action = ActivityLog.Action.UPDATED
                description = f"Lead {lead.full_name} was updated."
            log_activity(lead, request.user, action, description)
            messages.success(request, "Lead updated successfully.")
            return redirect(lead)
    else:
        form = LeadForm(instance=lead)
    return render(request, "crm/lead_form.html", {"form": form, "lead": lead, "title": "Edit Lead"})


@login_required
@require_POST
def lead_assign(request, pk):
    admin_required(request.user)
    lead = get_object_or_404(Lead, pk=pk)
    form = LeadAssignForm(request.POST, instance=lead)
    if form.is_valid():
        lead = form.save()
        log_activity(
            lead,
            request.user,
            ActivityLog.Action.ASSIGNED,
            f"Lead assigned to {lead.assigned_to or 'nobody'}.",
        )
        messages.success(request, "Lead assignment updated.")
    else:
        messages.error(request, "Unable to update lead assignment.")
    return redirect(lead)


@login_required
@require_POST
def lead_status_update(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if not can_update_status(request.user, lead):
        raise PermissionDenied
    previous_status = lead.status
    form = LeadStatusForm(request.POST, instance=lead)
    if form.is_valid():
        lead = form.save()
        if previous_status != lead.status:
            log_activity(
                lead,
                request.user,
                ActivityLog.Action.STATUS_CHANGED,
                f"Status changed to {lead.get_status_display()}.",
            )
        messages.success(request, "Lead status updated.")
    else:
        messages.error(request, "Unable to update lead status.")
    return redirect(lead)


@login_required
@require_POST
def lead_note_create(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if not can_add_note(request.user, lead):
        raise PermissionDenied
    form = LeadNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.lead = lead
        note.author = request.user
        note.save()
        log_activity(lead, request.user, ActivityLog.Action.NOTE_ADDED, "A note was added.")
        messages.success(request, "Note added.")
    else:
        messages.error(request, "Unable to add note.")
    return redirect(lead)


@login_required
@require_POST
def lead_delete(request, pk):
    if not request.user.is_admin_role:
        messages.error(request, "Only administrators can delete leads.")
        return redirect("lead_detail", pk=pk)

    lead = get_object_or_404(Lead, pk=pk)
    full_name = lead.full_name

    lead.delete()

    ActivityLog.objects.create(
        lead=None,
        actor=request.user,
        action=ActivityLog.Action.DELETED,
        description=f"Lead {full_name} was deleted.",
    )

    messages.success(request, "Lead deleted successfully.")
    return redirect("lead_list")
@login_required
def user_list(request):
    admin_required(request.user)
    users = User.objects.order_by("role", "username")
    query = request.GET.get("q", "").strip()
    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )
    return render(request, "crm/user_list.html", {"page_obj": paginate(request, users), "query": query})


@login_required
def user_create(request):
    admin_required(request.user)
    if request.method == "POST":
        form = CRMUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"User {user.username} created.")
            return redirect("user_list")
    else:
        form = CRMUserCreationForm(initial={"role": User.Role.MEMBER, "is_active": True})
    return render(request, "crm/user_form.html", {"form": form, "title": "Create User"})


@login_required
def user_update(request, pk):
    admin_required(request.user)
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = CRMUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"User {user.username} updated.")
            return redirect("user_list")
    else:
        form = CRMUserUpdateForm(instance=user)
    return render(request, "crm/user_form.html", {"form": form, "title": "Edit User", "managed_user": user})


@login_required
def activity_log(request):
    admin_required(request.user)
    activities = ActivityLog.objects.select_related("lead", "actor")
    query = request.GET.get("q", "").strip()
    action = request.GET.get("action", "").strip()
    if query:
        activities = activities.filter(
            Q(description__icontains=query)
            | Q(lead__full_name__icontains=query)
            | Q(actor__username__icontains=query)
        )
    if action:
        activities = activities.filter(action=action)
    context = {
        "page_obj": paginate(request, activities, per_page=15),
        "query": query,
        "selected_action": action,
        "action_choices": ActivityLog.Action.choices,
    }
    return render(request, "crm/activity_log.html", context)


def bad_request(request, exception):
    return render(
        request,
        "errors/400.html",
        {"status_code": 400, "title": "Bad Request"},
        status=400,
    )


def permission_denied(request, exception):
    return render(
        request,
        "errors/403.html",
        {"status_code": 403, "title": "Access Restricted"},
        status=403,
    )


def page_not_found(request, exception):
    return render(
        request,
        "errors/404.html",
        {"status_code": 404, "title": "Page Not Found"},
        status=404,
    )


def server_error(request):
    return render(
        request,
        "errors/500.html",
        {"status_code": 500, "title": "Something Went Wrong"},
        status=500,
    )
