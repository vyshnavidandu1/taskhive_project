from django import forms
from .models import Task
from users.models import User


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'assigned_user', 'priority', 'status', 'deadline')
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        if project:
            # Only project members can be assigned tasks
            member_ids = list(project.team_members.values_list('id', flat=True))
            member_ids.append(project.owner_id)
            self.fields['assigned_user'].queryset = User.objects.filter(
                id__in=member_ids, is_active=True
            )
        else:
            self.fields['assigned_user'].queryset = User.objects.filter(is_active=True)
        self.fields['assigned_user'].empty_label = '— Unassigned —'


class TaskFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All Statuses')] + list(Task.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'All Priorities')] + list(Task.PRIORITY_CHOICES)
    SORT_CHOICES = [
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
        ('deadline', 'Deadline (Earliest)'),
        ('-deadline', 'Deadline (Latest)'),
        ('priority', 'Priority (Low→High)'),
        ('-priority', 'Priority (High→Low)'),
        ('title', 'Title A–Z'),
    ]

    q = forms.CharField(required=False, label='Search', widget=forms.TextInput(attrs={
        'placeholder': 'Search tasks...', 'class': 'form-control'
    }))
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False,
                               widget=forms.Select(attrs={'class': 'form-select'}))
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False,
                                 widget=forms.Select(attrs={'class': 'form-select'}))
    assigned_user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        empty_label='All Assignees',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort = forms.ChoiceField(choices=SORT_CHOICES, required=False,
                             widget=forms.Select(attrs={'class': 'form-select'}))
