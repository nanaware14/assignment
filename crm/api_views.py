from rest_framework import generics, status
from rest_framework.response import Response

from .models import ActivityLog, Lead
from .permissions import LeadAPIPermission
from .serializers import LeadSerializer


def visible_leads_for(user):
    queryset = Lead.objects.select_related("assigned_to").prefetch_related("notes__author")
    if user.is_admin_role:
        return queryset
    return queryset.filter(assigned_to=user)


class LeadListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [LeadAPIPermission]
    filterset_fields = ["status", "priority", "source", "assigned_to"]
    search_fields = ["full_name", "email", "phone", "company", "source", "message"]
    ordering_fields = ["created_at", "updated_at", "status", "priority", "full_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Lead.objects.none()
        return visible_leads_for(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()
        actor = request.user if request.user.is_authenticated else None
        ActivityLog.objects.create(
            lead=lead,
            actor=actor,
            action=ActivityLog.Action.CREATED,
            description=f"Lead {lead.full_name} was created via API.",
        )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class LeadRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LeadSerializer
    permission_classes = [LeadAPIPermission]

    def get_queryset(self):
        return visible_leads_for(self.request.user)

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        previous_status = instance.status
        previous_assignee_id = instance.assigned_to_id
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()

        if previous_status != lead.status:
            ActivityLog.objects.create(
                lead=lead,
                actor=request.user,
                action=ActivityLog.Action.STATUS_CHANGED,
                description=f"Status changed to {lead.get_status_display()}.",
            )
        elif previous_assignee_id != lead.assigned_to_id:
            ActivityLog.objects.create(
                lead=lead,
                actor=request.user,
                action=ActivityLog.Action.ASSIGNED,
                description=f"Lead assigned to {lead.assigned_to or 'nobody'}.",
            )
        else:
            ActivityLog.objects.create(
                lead=lead,
                actor=request.user,
                action=ActivityLog.Action.UPDATED,
                description=f"Lead {lead.full_name} was updated.",
            )
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        lead = self.get_object()
        ActivityLog.objects.create(
            lead=None,
            actor=request.user,
            action=ActivityLog.Action.DELETED,
            description=f"Lead {lead.full_name} was deleted.",
        )
        lead.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
