from django.contrib import admin

from .. import forms
from .. import models


@admin.register(models.BankDeposit)
class BankDepositAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'check_amount', 'cash_amount']
    fields = ['datetime']
    form = forms.money_stock.BankDepositAdminForm

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def check_amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance,
            payment_type=models.MemberCommand.CHECK_PAYMENT
        )
        return sum(cmd.amount for cmd in commands)

    def cash_amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance,
            payment_type=models.MemberCommand.CASH_PAYMENT
        )
        treasury_ops = models.TreasuryOperation.objects.filter(
            bank_deposit=instance
        )
        return (sum(cmd.amount for cmd in commands) +
                sum(op.amount for op in treasury_ops))

@admin.register(models.TreasuryOperation)
class TreasuryOperationAdmin(admin.ModelAdmin):
    list_display = ['stock', 'bank_deposit']
    form = forms.money_stock.TreasuryOperationAdminForm
    fields = ['amount', 'with_bank_deposit']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
