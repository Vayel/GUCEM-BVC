from django import forms

from .. import models


class PlaceMemberCommand(forms.ModelForm):
    class Meta:
        model = models.MemberCommand
        fields = ['amount', 'spent_at_once',]


class MemberCommandAdminForm(forms.ModelForm):
    class Meta:
        model = models.MemberCommand
        fields = ['member', 'state', 'amount', 'spent_at_once',
                   'datetime_prepared', 'datetime_cancelled', 'datetime_sold',
                   'payment_type', 'bank_deposit',]

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if not amount:
            raise forms.ValidationError('The amount cannot be zero. Instead, cancel the command.')

        if (self.instance.state != models.command.PLACED_STATE and
            self.instance.state != models.command.TO_BE_PREPARED_STATE and
            self.instance.state != models.command.RECEIVED_STATE and
            self.instance.state != models.command.PREPARED_STATE):
           raise forms.ValidationError('The amount cannot be changed due to the command state.')

        self.old_amount = self.instance.amount

        if not models.voucher.is_delta_valid(self.old_amount - amount):
            raise forms.ValidationError("You don't have enough vouchers.")

        return amount

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.amount_changed(self.old_amount)

        if commit:
            instance.save()

        return instance
