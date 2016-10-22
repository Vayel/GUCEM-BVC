from django.contrib import admin, messages
from django.utils.timezone import now

from .. import models


class IndividualCommandAdmin(admin.ModelAdmin):
    actions = ['cancel']
    list_filter = ['state',]

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
    list_display = ['id', 'member', 'datetime_placed', 'amount', 'state',]
    actions = ['sell_by_check', 'sell_by_cash']
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
