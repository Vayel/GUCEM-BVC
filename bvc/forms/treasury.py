from django import forms

from .. import models


class TreasuryOperationAdminForm(forms.ModelForm):
    delta = forms.FloatField(initial=0)

    class Meta:
        model = models.TreasuryOperation
        fields = ['reason', 'delta',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is None:
            return

        self.fields['delta'].initial = self.instance.delta
        self.fields['delta'].disabled = True

    def clean_delta(self):
        treasury = models.treasury.get_treasury()
        delta = self.cleaned_data['delta']

        if treasury + delta < 0:
            raise forms.ValidationError("Il n'y a pas autant d'argent dans la caisse.")

        return delta

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.stock = models.treasury.get_treasury() + self.cleaned_data['delta']

        if commit:
            instance.save()

        return instance
