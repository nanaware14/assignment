from rest_framework import serializers

from .models import ActivityLog, Lead, LeadNote, User


class UserSummarySerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "full_name", "email", "role"]


class LeadNoteSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(read_only=True)

    class Meta:
        model = LeadNote
        fields = ["id", "author", "body", "created_at"]
        read_only_fields = ["id", "author", "created_at"]


class LeadSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSummarySerializer(source="assigned_to", read_only=True)
    notes = LeadNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "company",
            "source",
            "message",
            "status",
            "priority",
            "assigned_to",
            "assigned_to_detail",
            "created_at",
            "updated_at",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "assigned_to_detail", "notes"]

    def validate_assigned_to(self, value):
        if value and not value.is_member_role:
            raise serializers.ValidationError("Leads can only be assigned to members.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            attrs.pop("assigned_to", None)
            attrs.pop("priority", None)
            attrs.pop("status", None)
            return attrs

        if request.user.is_admin_role:
            return attrs

        if self.instance:
            disallowed = set(attrs) - {"status"}
            if disallowed:
                raise serializers.ValidationError("Members can only update the lead status.")
            return attrs

        attrs.pop("assigned_to", None)
        attrs.pop("priority", None)
        attrs.pop("status", None)
        return attrs


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = UserSummarySerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = ["id", "lead", "actor", "action", "description", "created_at"]
