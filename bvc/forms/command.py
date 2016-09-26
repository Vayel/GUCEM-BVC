from django.forms import ModelForm

from ..models import command

class PlaceMemberCommand(ModelForm):
    class Meta:
        model = command.MemberCommand
        fields = ['lastname', 'firstname', 'email', 'license', 'club',
                  'amount', 'comments',]

class PlaceCommissionCommand(ModelForm):
    class Meta:
        model = command.CommissionCommand
        fields = ['amount', 'commission', 'email', 'comments',]
