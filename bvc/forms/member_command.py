from django import forms

from .. import models


class PlaceMemberCommand(forms.ModelForm):
    class Meta:
        model = models.MemberCommand
        fields = ['amount', 'spent_at_once', 'comments',]
