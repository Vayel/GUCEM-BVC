from django import forms

from .. import models


class PlaceCommissionCommand(forms.ModelForm):
    commission = forms.ModelChoiceField(
        queryset=models.user.Commission.objects,
        empty_label=None,
    )

    class Meta:
        model = models.CommissionCommand
        fields = ['commission', 'amount', 'reason', 'spent_at_once', 'comments',]


class CommissionCommandAdminForm(forms.ModelForm):
    class Meta:
        model = models.CommissionCommand
        fields = ['commission', 'state', 'amount', 'reason', 'comments', 'spent_at_once',
                   'datetime_prepared', 'datetime_cancelled', 'datetime_given',]

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
