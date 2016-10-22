from django.contrib import admin, messages
from django.utils.timezone import now

from .. import models


class IndividualCommandAdmin(admin.ModelAdmin):
    actions = ['cancel']

@admin.register(models.MemberCommand)
class MemberCommandAdmin(IndividualCommandAdmin):
    list_display = ['id', 'member', 'datetime_placed', 'amount', 'state',]
    list_filter = ['state',]
    actions = ['sell_by_check', 'sell_by_cash']
    ordering = ['datetime_placed']

    def sell(self, request, queryset, payment_type):
        valid_commands = queryset.filter(state=models.command.PREPARED_STATE)
        # Use list for the queryset not to be updated below
        invalid_commands = list(queryset.exclude(state=models.command.PREPARED_STATE))

        valid_commands.update(
            state=models.command.SOLD_STATE,
            datetime_sold=now(),
            payment_type=payment_type,
        )

        for cmd in invalid_commands:
            self.message_user(
                request,
                "La commande {} ne peut être vendue car elle n'est pas "
                "préparée.".format(cmd),
                level=messages.WARNING,
            )

    def sell_by_check(self, request, queryset):
        self.sell(request, queryset, models.MemberCommand.CHECK_PAYMENT)

    def sell_by_cash(self, request, queryset):
        self.sell(request, queryset, models.MemberCommand.CASH_PAYMENT)
