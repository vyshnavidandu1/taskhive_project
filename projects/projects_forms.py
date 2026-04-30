from django import forms
from django.utils.html import format_html
from .models import Project, ProjectMembership
from users.models import User


class UserCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Custom widget that renders user checkboxes with full name and role badge."""

    def create_option(self, name, value, label, selected, index, subgroup=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subgroup, attrs)
        # Get the user object to show richer label
        try:
            user = User.objects.get(pk=value)
            full_name = user.get_full_name() or user.username
            role = user.get_role_display()
            option['label'] = f"{full_name} (@{user.username}) — {role}"
        except (User.DoesNotExist, ValueError, TypeError):
            pass
        return option


class ProjectForm(forms.ModelForm):
    team_members_input = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=UserCheckboxSelectMultiple,
        required=False,
        label='Team Members'
    )

    class Meta:
        model = Project
        fields = ('name', 'description', 'status', 'start_date', 'end_date')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, (forms.CheckboxSelectMultiple, UserCheckboxSelectMultiple)):
                continue
            field.widget.attrs['class'] = 'form-control'
        if self.instance.pk:
            self.fields['team_members_input'].initial = self.instance.team_members.all()
            if self.user:
                self.fields['team_members_input'].queryset = User.objects.filter(
                    is_active=True
                ).exclude(id=self.instance.owner_id)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError('End date must be after start date.')
        return cleaned_data

    def save_members(self, project):
        members = self.cleaned_data.get('team_members_input', [])
        ProjectMembership.objects.filter(project=project).exclude(user=project.owner).delete()
        for member in members:
            if member != project.owner:
                ProjectMembership.objects.get_or_create(
                    project=project, user=member,
                    defaults={'role': 'member'}
                )
