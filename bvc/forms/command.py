from django import forms
from django.utils.timezone import now
from django.contrib import messages

from .. import models


class GroupedCommandAdmin(forms.ModelForm):
    amount = forms.IntegerField(
        min_value=0,
        validators=[models.validators.validate_amount_multiple],
        label='Montant',
    )

    class Meta:
        model = models.command.GroupedCommand
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)

        if instance is not None:
            if instance.datetime_placed is None:
                self.fields['amount'].label = instance._meta.get_field('placed_amount').verbose_name
            elif instance.datetime_received is None:
                self.fields['amount'].label = instance._meta.get_field('received_amount').verbose_name
            elif instance.datetime_prepared is None:
                self.fields['amount'].label = instance._meta.get_field('prepared_amount').verbose_name
            else:
                self.fields['amount'].widget = forms.HiddenInput()
                self.fields['amount'].required = False

    def clean_received_amount(self):
        amount = self.cleaned_data['amount'] or 0

        try:
            self.instance.check_next(amount)
        except ValueError as e:
            raise ValidationError(e.msg)

        return amount

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.next(self.cleaned_data['amount'])

        if commit:
            instance.save()

        return instance
