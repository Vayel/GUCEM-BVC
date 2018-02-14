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
        fields = ['bank_deposit']
    
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
    n10 = forms.IntegerField(
        min_value=0,
        label='Nombre de billets de 10',
    )
    n20 = forms.IntegerField(
        min_value=0,
        label='Nombre de billets de 20',
    )
    n50 = forms.IntegerField(
        min_value=0,
        label='Nombre de billets de 50',
    )
    amount = forms.IntegerField(
        disabled=True,
        required=False,
        label='Total',
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        if instance:
            kwargs.update(initial={
                'amount': instance.total_price
            })
        super().__init__(*args, **kwargs)

    class Meta:
        model = models.CashBankDeposit
        fields = ['bank_deposit', 'n10', 'n20', 'n50', 'amount',]

    def get_amount(self):
        return sum(self.cleaned_data['n' + str(n)] * n for n in (10, 20, 50))

    def clean(self):
        cleaned_data = super().clean()
        try:
            amount = self.get_amount()
        except KeyError:
            return

        if models.member_command.get_available_cash_amount() - amount < 0:
            raise forms.ValidationError("Il n'y a pas autant d'argent liquide à disposition.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        treasury = models.treasury.get_treasury()
        amount = self.get_amount()
        total = models.member_command.get_available_cash_amount()
        treasury_delta = total - treasury - amount

        # Create the treasury operation
        instance.treasury_operation = models.treasury.treasury_op_from_delta(
            treasury_delta,
            'BVE {}'.format(models.CashBankDeposit.next_id()),
        )

        models.member_command.bank_commands(
            models.command.CASH_PAYMENT,
            self.cleaned_data['bank_deposit']
        )

        if commit:
            instance.save()

        return instance
