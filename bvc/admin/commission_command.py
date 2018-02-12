from smtplib import SMTPException

from django.contrib import admin, messages
from django.utils.timezone import now

from .site import admin_site
from .individual_command import IndividualCommandAdmin
from .. import models, forms


class CommissionCommandAdmin(IndividualCommandAdmin):
    list_display = ['id', 'commission', 'datetime_placed', 'amount', 'state',
                    'reason',]
    ordering = ['datetime_placed']
    search_fields = ('commission__user__username',)
    fields = forms.commission_command.CommissionCommandAdminForm.Meta.fields
    form = forms.commission_command.CommissionCommandAdminForm
    
    def get_readonly_fields(self, request, instance=None):
        if instance: # Editing an existing object
            fields = self.fields + []

            if (instance.state == models.command.PLACED_STATE or
                instance.state == models.command.TO_BE_PREPARED_STATE or
                instance.state == models.command.RECEIVED_STATE or
                instance.state == models.command.PREPARED_STATE):

                fields.remove('amount')

            return fields

        return self.readonly_fields or []

    def get_inline_actions(self, request, obj=None):
        actions = super().get_inline_actions(request, obj)
        if obj is None:
            return actions
        if obj.state == models.command.PREPARED_STATE:
            actions.append('distribute')
        return actions

    def get_distribute_label(self, obj):
        return "Distribuer"

    def distribute(self, request, cmd, parent_obj=None):
        try:
            cmd.distribute()
        except models.command.InvalidState:
            self.message_user(
                request,
                "La commande {} n'est pas dans le bon état pour être distribuée.".format(cmd),
                level=messages.ERROR
            )
        except SMTPException as e:
            self.message_user(
                request,
                "Une erreur est survenue en envoyant le mail : " + str(e),
                level=messages.ERROR
            )


admin_site.register(models.CommissionCommand, CommissionCommandAdmin)
