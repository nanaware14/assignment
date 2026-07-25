from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Lead, LeadNote, User


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = "form-check-input"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css_class}".strip()
            if field.required:
                field.widget.attrs.setdefault("required", True)


class LeadCaptureForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["full_name", "email", "phone", "company", "source", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }


class LeadForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "full_name",
            "email",
            "phone",
            "company",
            "source",
            "message",
            "status",
            "priority",
            "assigned_to",
        ]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(
            role=User.Role.MEMBER,
            is_active=True,
        ).order_by("first_name", "last_name", "username")
        self.fields["assigned_to"].required = False


class LeadStatusForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["status"]


class LeadAssignForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["assigned_to"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(
            role=User.Role.MEMBER,
            is_active=True,
        ).order_by("first_name", "last_name", "username")


class LeadNoteForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = LeadNote
        fields = ["body"]
        labels = {"body": "Note"}
        widgets = {
            "body": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a note"}),
        }


class CRMUserCreationForm(BootstrapFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "role", "is_active")


class CRMUserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "role", "is_active")
