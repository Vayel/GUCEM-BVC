from django import forms

from .. import models


class PlaceMemberCommand(forms.ModelForm):
    class Meta:
        model = models.MemberCommand
        fields = ['amount', 'comments',]
