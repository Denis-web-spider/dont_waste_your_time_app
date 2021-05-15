from django import forms
from django.forms.utils import ErrorList

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Activities, Projects, Tasks

from datetime import timedelta, datetime

class DivErrorList(ErrorList):

    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self.data:
            return ''

        return ''.join([f'<div>{e}</div>' for e in self])

class ActivitiesForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].queryset = Activities.objects.activities(user=user)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'data-bs-toggle': 'tooltip',
                'data-bs-placement': 'bottom',
                'title': self.fields[field_name].label,
                'placeholder': self.fields[field_name].label,
            })

        self.fields['color'].widget = forms.TextInput(attrs={
            'type': 'color',
            'class': 'form-control form-control-lg form-control-color',
        })

    class Meta:
        model = Activities
        fields = ['title', 'color', 'parent']

class ProjectsForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['activity'].queryset = Activities.objects.activities(user=user)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'data-bs-toggle': 'tooltip',
                'data-bs-placement': 'bottom',
                'title': self.fields[field_name].label,
                'placeholder': self.fields[field_name].label,
            })

        self.fields['color'].widget = forms.TextInput(attrs={
            'type': 'color',
            'class': 'form-control form-control-lg form-control-color',
        })

    class Meta:
        model = Projects
        fields = ['title', 'color', 'activity']

class ChangeProjectForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['activity'].queryset = Activities.objects.activities(user=user)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control form-control-lg',
                'data-bs-toggle': 'tooltip',
                'data-bs-placement': 'bottom',
                'title': self.fields[field_name].label,
                'placeholder': self.fields[field_name].label,
            })

        self.fields['color'].widget = forms.TextInput(attrs={
            'type': 'color',
            'class': 'form-control form-control-lg form-control-color',
        })

    class Meta:
        model = Projects
        fields = ['title', 'color', 'status', 'activity']

class TasksForm(forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
            })

        self.fields['title'].widget.attrs.update({
            'placeholder': self.fields['title'].label,
        })

        self.fields['start'].widget.input_type = 'time'
        self.fields['end'].widget.input_type = 'time'
        self.fields['duration'].widget.input_type = 'time'
        self.fields['date'].widget.input_type = 'date'

        self.fields['activity'].queryset = Activities.objects.activities(user=user)
        self.fields['project'].queryset = Projects.objects.projects(user=user).filter(finished=None)
        
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'data-bs-toggle': 'tooltip',
                'data-bs-placement': 'bottom',
                'title': self.fields[field_name].label,
            })

    class Meta:
        model = Tasks
        fields = [
            'title',
            'project',
            'activity',
            'start',
            'end',
            'date',
            'duration'
        ]

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data['start']
        end = cleaned_data['end']
        duration = cleaned_data['duration']

        end_subtract_start_timedelta = timedelta(hours=end.hour - start.hour, minutes=end.minute - start.minute)
        duration_timedelta = timedelta(hours=duration.hour, minutes=duration.minute)

        if end_subtract_start_timedelta < timedelta():
            raise ValidationError(_('Конец задачи должен быть после его начала'))

        if end_subtract_start_timedelta != duration_timedelta:
            raise ValidationError(_('Продолжительность задачи не совпадает с разницей её начала и конца'))
