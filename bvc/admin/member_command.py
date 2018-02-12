from smtplib import SMTPException

from django.contrib import admin, messages
from django.utils.timezone import now

from .site import admin_site
from .individual_command import IndividualCommandAdmin
from .. import models, forms


class MemberCommandAdmin(IndividualCommandAdmin):
    list_display = ['id', 'member', 'datetime_placed', 'amount', 'price',
                    'payment_type', 'state',]
    ordering = ['datetime_placed']
    search_fields = ('member__user__first_name', 'member__user__last_name', 'amount')
    fields = forms.member_command.MemberCommandAdminForm.Meta.fields
    form = forms.member_command.MemberCommandAdminForm

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
            actions.extend(('sell_by_check', 'sell_by_cash'))
        if obj.state in (models.command.SOLD_STATE, models.command.TO_BE_BANKED_STATE):
            actions.append('cancel_sale')
        if obj.state == models.command.SOLD_STATE:
            actions.append('add_to_bank_deposit')
        if obj.state == models.command.TO_BE_BANKED_STATE and obj.payment_type not in obj.AUTO_BANKED_PAYMENT_TYPES:
            actions.append('remove_from_bank_deposit')

        return actions

    def price(self, instance):
        return instance.price

    price.short_description = "Prix"

    def sell(self, request, cmd, payment_type):
        try:
            cmd.sell(payment_type)
        except models.command.InvalidState:
            self.message_user(
                request,
                "La commande {} n'est pas dans le bon état pour être vendue.".format(cmd),
                level=messages.ERROR
            )
        except SMTPException as e:
            self.message_user(
                request,
                "Une erreur est survenue en envoyant le mail : " + str(e),
                level=messages.ERROR
            )

    def get_sell_by_check_label(self, obj):
        return "Vendre par chèque"

    def sell_by_check(self, request, cmd, parent_obj=None):
        self.sell(request, cmd, models.command.CHECK_PAYMENT)

    def get_sell_by_cash_label(self, obj):
        return "Vendre par espèces"

    def sell_by_cash(self, request, cmd, parent_obj=None):
        self.sell(request, cmd, models.command.CASH_PAYMENT)

    def get_cancel_sale_label(self, obj):
        return "Annuler la vente"

    def cancel_sale(self, request, queryset):
        for cmd in queryset:
            try:
                cmd.cancel_sale()
            except models.command.InvalidState:
                self.message_user(
                    request,
                    "La commande {} n'est pas dans le bon état pour en annuler la vente.".format(cmd),
                    level=messages.ERROR
                )

    def get_add_to_bank_deposit_label(self, obj):
        return "Intégrer au dépôt"

    def add_to_bank_deposit(self, request, cmd, parent_obj=None):
        try:
            cmd.add_to_bank_deposit()
        except models.command.InvalidState:
            self.message_user(
                request,
                "La commande {} n'est pas dans le bon état pour être déposée en banque.".format(cmd),
                level=messages.ERROR
            )
        except SMTPException as e:
            self.message_user(
                request,
                "Une erreur est survenue en envoyant le mail : " + str(e),
                level=messages.ERROR
            )

    def get_remove_from_bank_deposit_label(self, obj):
        return "Enlever du dépôt"

    def remove_from_bank_deposit(self, request, cmd, parent_obj=None):
        try:
            cmd.remove_from_bank_deposit()
        except models.command.InvalidState:
            self.message_user(
                request,
                "La commande {} n'est pas dans le bon état pour être retirée d'un dépôt en banque.".format(cmd),
                level=messages.ERROR
            )
        except models.command.InvalidPaymentType:
            self.message_user(
                request,
                "La commande {} ne peut être retirée du dépôt en banque du fait de son type de paiment ({}).".format(cmd, cmd.payment_type),
                level=messages.ERROR
            )
        except SMTPException as e:
            self.message_user(
                request,
                "Une erreur est survenue en envoyant le mail : " + str(e),
                level=messages.ERROR
            )


admin_site.register(models.MemberCommand, MemberCommandAdmin)
