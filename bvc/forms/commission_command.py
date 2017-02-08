from django import forms

from .. import models


class PlaceCommissionCommand(forms.ModelForm):
    commission = forms.ModelChoiceField(
        queryset=models.user.Commission.objects,
        empty_label=None,
    )

    class Meta:
        model = models.CommissionCommand
        fields = ['commission', 'amount', 'reason', 'comments',]
