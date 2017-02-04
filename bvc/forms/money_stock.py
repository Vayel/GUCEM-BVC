from django import forms
from django.utils.timezone import now
from django.conf import settings

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


class CheckBankDepositAdminForm(forms.ModelForm):
    class Meta:
        model = models.CheckBankDeposit
        exclude = []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        models.individual_command.bank_commands(
            models.command.CHECK_PAYMENT,
            self.cleaned_data['bank_deposit']
        )

        if commit:
            instance.save()

        return instance


class CashBankDepositAdminForm(BankDepositAdminForm):
    amount = forms.IntegerField(
        min_value=settings.BANK_DEPOSIT_CASH_MULTIPLE,
        max_value=models.individual_command.get_available_cash_amount(),
        validators=[models.validators.validate_cash_amount_multiple],
    )

    class Meta:
        model = models.CashBankDeposit
        exclude = ['treasury_operation']
        
    def save(self, commit=True):
        instance = super().save(commit=False)

        # Create the treasury operation
        delta = (self.fields['amount'].max_value - models.money_stock.get_treasury() -
                 self.cleaned_data['amount'])
        instance.treasury_operation = models.money_stock.treasury_op_from_delta(delta)

        models.individual_command.bank_commands(
            models.command.CASH_PAYMENT,
            self.cleaned_data['bank_deposit']
        )

        if commit:
            instance.save()

        return instance


class TreasuryOperationAdminForm(forms.ModelForm):
    amount = forms.FloatField(initial=0)

    class Meta:
        model = models.TreasuryOperation
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.id is None:
            return

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

        instance.stock = models.money_stock.get_treasury() + self.cleaned_data['amount']

        if commit:
            instance.save()

        return instance
