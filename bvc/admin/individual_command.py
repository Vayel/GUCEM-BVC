from django.contrib import admin, messages
from django.utils.timezone import now

from .. import models


class IndividualCommandAdmin(admin.ModelAdmin):
    actions = ['cancel']
    list_filter = ['state',]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def cancel(self, request, queryset):
        for cmd in queryset:
            try:
                cmd.cancel()
            except models.command.InvalidState:
                self.message_user(
                    request,
                    "La commande {} n'est pas dans le bon état pour être annulée.".format(cmd),
                    level=messages.ERROR
                )

@admin.register(models.MemberCommand)
class MemberCommandAdmin(IndividualCommandAdmin):
    list_display = ['id', 'member', 'datetime_placed', 'amount', 'payment_type',
                    'bank_deposit', 'state',]
    actions = ['sell_by_check', 'sell_by_cash', 'add_to_bank_deposit',
               'remove_from_bank_deposit']
    ordering = ['datetime_placed']

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

    def sell_by_check(self, request, queryset):
        self.sell(request, queryset, models.MemberCommand.CHECK_PAYMENT)

    def sell_by_cash(self, request, queryset):
        self.sell(request, queryset, models.MemberCommand.CASH_PAYMENT)
        
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


@admin.register(models.CommissionCommand)
class CommissionCommandAdmin(IndividualCommandAdmin):
    list_display = ['id', 'commission', 'datetime_placed', 'amount', 'state',]
    actions = ['distribute',]
    ordering = ['datetime_placed']

    def distribute(self, request, queryset):
        for cmd in queryset:
            try:
                cmd.distribute()
            except models.command.InvalidState:
                self.message_user(
                    request,
                    "La commande {} n'est pas dans le bon état pour être distribuée.".format(cmd),
                    level=messages.ERROR
                )
