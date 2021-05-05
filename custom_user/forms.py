from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)

from django.utils.translation import gettext, gettext_lazy as _

User = get_user_model()

class RegistrationForm(forms.Form):
    email = forms.EmailField(label=_('Email'))
    password = forms.CharField(widget=forms.PasswordInput, label=_('Пароль'))

    email.widget.attrs.update({
        'placeholder': f'{email.label}',
    })
    password.widget.attrs.update({
        'placeholder': f'{password.label}',
    })

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(gettext('Пользователь с данным email уже зарегистрирован'))
        return email

class MyAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'placeholder': self.fields['username'].label
        })

        self.fields['password'].widget.attrs.update({
            'placeholder': self.fields['password'].label
        })

class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'placeholder': self.fields[field].label
            })

class MyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'placeholder': self.fields[field].label
            })

class MySetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'placeholder': self.fields[field].label
            })

class PersonalInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'placeholder': self.fields[field_name].label,
            })

    class Meta:
        model = User
        fields = ['email']
