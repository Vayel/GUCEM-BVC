from django.contrib.auth.models import User
from django import forms

from .. import models


class MemberUserCommand(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'last_name', 'first_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    def clean_email(self):
        """Check if the email is already used by a commission."""
        email = self.cleaned_data['email']

        for com in models.user.Commission.objects.all():
            if com.user.email == email:
                raise forms.ValidationError('Cet email est déjà utilisé par une commission.'
                                            ' Merci de renseigner une adresse personnelle.')

        return email


class MemberCommand(forms.ModelForm):
    class Meta:
        model = models.user.Member
        fields = ['license', 'club']
        labels = {
            'license': 'Licence CAF'
        }


class CommandSummary(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email',]


class GroupedCommandReminder(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email',]
