from django import forms
from django.utils.timezone import now

from .. import models


class BankDepositAdminForm(forms.ModelForm):
    class Meta:
        model = models.BankDeposit
        exclude = []

    def clean_datetime(self):
        datetime = self.cleaned_data['datetime']

        if datetime > now():
            raise forms.ValidationError('La date de dépôt ne peut être dans le '
                                        'futur.')

        return datetime

    def save(self, commit=True):
        instance = super().save(commit=False)
        old_datetime = models.BankDeposit.objects.get(id=instance.id).datetime

        if old_datetime is None and instance.datetime is not None: # The bank deposit was done
            models.individual_command.cash_commands()
            models.BankDeposit.objects.create()

        if commit:
            instance.save()

        return instance
