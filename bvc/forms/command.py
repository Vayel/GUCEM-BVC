from django import forms

from .. import models


class GroupedCommandAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.fields['datetime_received'].required = True
        except KeyError:
            pass
        try:
            self.fields['datetime_prepared'].required = True
        except KeyError:
            pass

    class Meta:
        model = models.GroupedCommand
        fields = ['state', 'datetime_placed', 'placed_amount', 'datetime_received',
                  'received_amount', 'datetime_prepared', 'prepared_amount',]

    def clean_amount_field(self, state, prev_state):
        amount = self.cleaned_data[state + '_amount']

        if not amount:
            raise forms.ValidationError('The amount cannot be zero.')

        prev_amount = self.instance.__dict__[prev_state + '_amount']
        if amount > prev_amount:
            raise forms.ValidationError(
                'The {} amount cannot be greater than '
                'the {} amount.'.format(state, prev_state)
            )

        self.amount = amount
        return amount

    def clean_date_field(self, state, prev_state):
        date = self.cleaned_data['datetime_' + state]

        prev = self.instance.__dict__['datetime_' + prev_state]
        if date <= prev:
            raise forms.ValidationError(
                'The {} date cannot be older than '
                'the {} date.'.format(state, prev_state)
            )

        self.date = date
        return date

    def check_state(self, state, callback):
        if self.instance.__dict__['state'] != state:
            raise forms.ValidationError("La commande n'est pas dans le bon état.")

        self.callback = callback

    def clean_received_amount(self):
        self.check_state(models.command.PLACED_STATE, self.instance.receive)
        amount = self.cleaned_data['received_amount']

        if not amount:
            raise forms.ValidationError('The amount cannot be zero.')

        self.amount = amount
        return amount

    def clean_datetime_received(self):
        self.check_state(models.command.PLACED_STATE, self.instance.receive)
        return self.clean_date_field('received', 'placed')

    def clean_prepared_amount(self):
        self.check_state(models.command.RECEIVED_STATE, self.instance.prepare_)
        return self.clean_amount_field('prepared', 'received')

    def clean_datetime_prepared(self):
        self.check_state(models.command.RECEIVED_STATE, self.instance.prepare_)
        return self.clean_date_field('prepared', 'received')

    def save(self, commit=True):
        instance = super().save(commit=False)
        self.callback(self.amount, self.date)

        if commit:
            instance.save()

        return instance


class PlaceGroupedCommand(forms.ModelForm):
    class Meta:
        model = models.GroupedCommand
        fields = ['placed_amount',]


class PlaceMemberCommand(forms.ModelForm):
    class Meta:
        model = models.MemberCommand
        fields = ['amount', 'comments',]


class PlaceCommissionCommand(forms.ModelForm):
    commission = forms.ModelChoiceField(
        queryset=models.user.Commission.objects,
        empty_label=None,
    )

    class Meta:
        model = models.CommissionCommand
        fields = ['commission', 'amount', 'reason', 'comments',]
