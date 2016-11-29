from django.contrib import admin

from .. import forms
from .. import models


@admin.register(models.BankDeposit)
class BankDepositAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'datetime', 'ref']
    fields = ['datetime', 'ref',]
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


@admin.register(models.CheckBankDeposit)
class CheckBankDepositAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'amount']
    form = forms.money_stock.CheckBankDepositAdminForm
 
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance.bank_deposit,
        )
        return sum(cmd.amount for cmd in commands)


@admin.register(models.CashBankDeposit)
class CashBankDepositAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'amount']
    form = forms.money_stock.CashBankDepositAdminForm
 
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance.bank_deposit,
        )
        treasury_ops = models.TreasuryOperation.objects.filter(
            bank_deposit=instance
        )
        return (sum(cmd.amount for cmd in commands) +
                sum(-op.amount for op in treasury_ops))


@admin.register(models.TreasuryOperation)
class TreasuryOperationAdmin(admin.ModelAdmin):
    list_display = ['stock']
    form = forms.money_stock.TreasuryOperationAdminForm
    fields = ['amount']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
