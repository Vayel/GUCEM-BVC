from django.forms import ModelForm, ValidationError

from ..models import command

class PlaceMemberCommand(ModelForm):
    class Meta:
        model = command.MemberCommand
        fields = ['amount', 'comments',]

class PlaceCommissionCommand(ModelForm):
    class Meta:
        model = command.CommissionCommand
        fields = ['amount', 'comments',]

class PlaceGroupedCommand(ModelForm):
    class Meta:
        model = command.GroupedCommand
        fields = ['placed_amount']
        
class ReceiveGroupedCommand(ModelForm):
    class Meta:
        model = command.GroupedCommand
        fields = ['received_amount']

    def clean_received_amount(self):
        received_amount = self.cleaned_data['received_amount']

        if received_amount > self.instance.placed_amount:
            raise ValidationError('Le montant reçu ne peut être supérieur à ' +
                                  'celui commandé')

        return received_amount

class PrepareGroupedCommand(ModelForm):
    class Meta:
        model = command.GroupedCommand
        fields = ['prepared_amount']
