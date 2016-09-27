from django.forms import ModelForm

from ..models import command

class PlaceMemberCommand(ModelForm):
    class Meta:
        model = command.MemberCommand
        fields = ['amount', 'comments',]

class PlaceCommissionCommand(ModelForm):
    class Meta:
        model = command.CommissionCommand
        fields = ['amount', 'comments',]
