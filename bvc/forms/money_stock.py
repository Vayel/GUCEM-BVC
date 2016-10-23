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


class TreasuryOperationAdminForm(forms.ModelForm):
    amount = forms.FloatField(initial=0)
    with_bank_deposit = forms.BooleanField(required=False, initial=True,)

    class Meta:
        model = models.TreasuryOperation
        fields = ['amount', 'with_bank_deposit']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is None:
            return

        self.fields['with_bank_deposit'].initial = self.instance.bank_deposit != None
        self.fields['with_bank_deposit'].disabled = True
        self.fields['amount'].initial = self.instance.amount
        self.fields['amount'].disabled = True

    def clean_amount(self):
        treasury = models.money_stock.get_treasury()
        amount = self.cleaned_data['amount']

        if treasury + amount < 0:
            raise forms.ValidationError("Il n'y a pas autant d'argent dans la caisse.")

        return amount

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data['with_bank_deposit']:
            instance.bank_deposit = models.money_stock.get_current_bank_deposit()
        else:
            instance.bank_deposit = None

        instance.stock = models.money_stock.get_treasury() + self.cleaned_data['amount']

        if commit:
            instance.save()

        return instance
