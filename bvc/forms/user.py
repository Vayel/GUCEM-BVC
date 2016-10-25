from django.contrib.auth.models import User
from django import forms

from .. import models


class MemberUserCommand(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'last_name', 'first_name']


class MemberCommand(forms.ModelForm):
    class Meta:
        model = models.user.Member
        fields = ['license', 'club']
