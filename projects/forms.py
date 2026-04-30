from django import forms
from .models import Project, ProjectMembership
from users.models import User


class ProjectForm(forms.ModelForm):
    team_members_input = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
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
            if isinstance(field.widget, (forms.CheckboxSelectMultiple,)):
                continue
            field.widget.attrs['class'] = 'form-control'
        if self.instance.pk:
            self.fields['team_members_input'].initial = self.instance.team_members.all()
            # Exclude owner from team members selection
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
        # Clear existing memberships (except owner's if present)
        ProjectMembership.objects.filter(project=project).exclude(user=project.owner).delete()
        for member in members:
            if member != project.owner:
                ProjectMembership.objects.get_or_create(
                    project=project, user=member,
                    defaults={'role': 'member'}
                )
