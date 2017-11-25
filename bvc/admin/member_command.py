from smtplib import SMTPException

from django.contrib import admin, messages
from django.utils.timezone import now

from .site import admin_site
from .individual_command import IndividualCommandAdmin
from .. import models, forms


class MemberCommandAdmin(IndividualCommandAdmin):
    list_display = ['id', 'member', 'datetime_placed', 'amount', 'price',
                    'payment_type', 'state', 'voucher_distrib', 'spent_at_once',
                    'comments',]
    actions = ['sell_by_check', 'sell_by_cash', 'cancel_sale', 'add_to_bank_deposit',
               'remove_from_bank_deposit']
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

    def sell(self, request, queryset, payment_type):
        for cmd in queryset:
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

    def sell_by_check(self, request, queryset):
        self.sell(request, queryset, models.command.CHECK_PAYMENT)

    def sell_by_cash(self, request, queryset):
        self.sell(request, queryset, models.command.CASH_PAYMENT)

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

    def add_to_bank_deposit(self, request, queryset):
        for cmd in queryset:
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

    def remove_from_bank_deposit(self, request, queryset):
        for cmd in queryset:
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
