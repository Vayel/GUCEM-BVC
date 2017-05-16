from django import forms
from django.conf import settings

from .. import models


class BankDepositAdminForm(forms.ModelForm):
    class Meta:
        model = models.BankDeposit
        exclude = ['made']


class CheckBankDepositAdminForm(forms.ModelForm):
    class Meta:
        model = models.CheckBankDeposit
        exclude = []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        models.member_command.bank_commands(
            models.command.CHECK_PAYMENT,
            self.cleaned_data['bank_deposit']
        )

        if commit:
            instance.save()

        return instance


class CashBankDepositAdminForm(BankDepositAdminForm):
    amount = forms.IntegerField(
        min_value=settings.BANK_DEPOSIT_CASH_MULTIPLE,
        validators=[models.validators.validate_cash_amount_multiple],
        label='Montant',
    )

    class Meta:
        model = models.CashBankDeposit
        exclude = ['treasury_operation']

    def get_delta(self):
        return (models.member_command.get_available_cash_amount() -
                models.treasury.get_treasury() - self.cleaned_data['amount'])

    def clean_amount(self):
        treasury = models.treasury.get_treasury()

        if treasury + self.get_delta() < 0:
            raise forms.ValidationError("Il n'y a pas autant d'argent liquide à disposition.")

        return self.cleaned_data['amount']

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Create the treasury operation
        last_deposit = models.CashBankDeposit.objects.last()
        instance.treasury_operation = models.treasury.treasury_op_from_delta(
            self.get_delta(),
            'BVE {}'.format(last_deposit.id + 1 if last_deposit is not None else 1),
        )

        models.member_command.bank_commands(
            models.command.CASH_PAYMENT,
            self.cleaned_data['bank_deposit']
        )

        if commit:
            instance.save()

        return instance
