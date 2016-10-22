from django import forms
from django.utils.timezone import now
from django.contrib import messages

from .. import models

def clean_amount(state, prev_state):
    def decorator(func):
        def wrapper(form):
            amount = form.cleaned_data[state + '_amount']
            if amount is None:
                return amount
            
            prev_amount = form.instance.__dict__[prev_state + '_amount']
            if amount > prev_amount:
                raise forms.ValidationError(
                    'The {} amount cannot be greater than '
                    'the {} amount.'.format(state, prev_state)
                )
            if not amount:
                raise forms.ValidationError('The amount cannot be zero.')

            func(form, amount)

            return amount
        return wrapper
    return decorator

class GroupedCommandAdmin(forms.ModelForm):
    class Meta:
        model = models.GroupedCommand
        fields = ['state', 'datetime_placed', 'placed_amount', 'datetime_received',
                  'received_amount', 'datetime_prepared', 'prepared_amount',]

    def clean_placed_amount(self, amount):
        self.instance.place(amount)

    @clean_amount('received', 'placed')
    def clean_received_amount(self, amount):
        self.instance.receive(amount)

    @clean_amount('prepared', 'received')
    def clean_prepared_amount(self, amount):
        self.instance.prepare_(amount)
