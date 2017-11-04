from django import forms
from django.utils.timezone import now

from .. import models


class GroupedCommandAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        if instance:
            if instance.state == models.command.PLACED_STATE:
                kwargs.update(initial={
                    'datetime_transmitted': now()
                })
            elif instance.state == models.command.TRANSMITTED_STATE:
                kwargs.update(initial={
                    'received_amount': instance.placed_amount,
                    'datetime_received': now(),
                })
            elif instance.state == models.command.RECEIVED_STATE:
                kwargs.update(initial={
                    'datetime_prepared': now(),
                })

        super().__init__(*args, **kwargs)

        self.amount = self.date = None

        try:
            self.fields['datetime_transmitted'].required = True
        except KeyError:
            pass
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
        fields = ['state', 'datetime_placed', 'placed_amount', 'datetime_transmitted',
                  'datetime_received', 'received_amount', 'datetime_prepared',]

    def clean_amount_field(self, state):
        amount = self.cleaned_data[state + '_amount']

        if not amount:
            raise forms.ValidationError('The amount cannot be zero.')

        self.amount = amount
        return amount

    def clean_date_field(self, state, prev_state):
        date = self.cleaned_data['datetime_' + state]

        prev = self.instance.__dict__['datetime_' + prev_state]
        try:
            prev_date = prev.date()
        except AttributeError:
            prev_date = prev

        if date < prev_date:
            raise forms.ValidationError(
                'The {} date cannot be older than '
                'the {} date.'.format(state, prev_state)
            )

        self.date = date
        return date

    def check_state(self, state):
        if self.instance.state != state:
            raise forms.ValidationError("La commande n'est pas dans le bon état.")

    def clean_placed_amount(self):
        unprepared_cmd = models.GroupedCommand.objects.exclude(
            state=models.command.PREPARED_STATE
        )
        if unprepared_cmd.count():
            raise forms.ValidationError("Une commande groupée est déjà en cours.")

        amount = self.cleaned_data['placed_amount']
        if amount < models.grouped_command.min_amount_to_place():
            raise forms.ValidationError("Le montant ne permet pas de satisfaire "
                                        "toutes les commandes.")

        self.amount = amount
        return amount

    def clean_datetime_transmitted(self):
        self.check_state(models.command.PLACED_STATE)
        return self.clean_date_field('transmitted', 'placed')

    def clean_received_amount(self):
        self.check_state(models.command.TRANSMITTED_STATE)
        return self.clean_amount_field('received')

    def clean_datetime_received(self):
        self.check_state(models.command.TRANSMITTED_STATE)
        return self.clean_date_field('received', 'transmitted')

    def clean_datetime_prepared(self):
        self.check_state(models.command.RECEIVED_STATE)
        return self.clean_date_field('prepared', 'received')

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.state is None:
            instance.place(self.amount)
        elif instance.state == models.command.PLACED_STATE:
            instance.transmit(self.date)
        elif instance.state == models.command.TRANSMITTED_STATE:
            instance.receive(self.amount, self.date)
        elif instance.state == models.command.RECEIVED_STATE:
            instance.prepare_(self.date)

        if commit:
            instance.save()

        return instance
