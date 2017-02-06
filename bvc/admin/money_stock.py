from django.contrib import admin

from .site import admin_site
from .. import forms
from .. import models


class BankDepositAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

class CheckBankDepositAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__', 'amount']
    form = forms.money_stock.CheckBankDepositAdminForm
 
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        extra_context['to_be_banked_check_number'] = models.MemberCommand.objects.filter(
            state=models.command.TO_BE_BANKED_STATE,
            payment_type=models.command.CHECK_PAYMENT,
        ).count()
        extra_context['not_to_be_banked_check_number'] = models.MemberCommand.objects.filter(
            state=models.command.SOLD_STATE,
            payment_type=models.command.CHECK_PAYMENT,
        ).count()
        extra_context['to_be_banked_check_total_amount'] = sum(cmd.price
            for cmd in models.MemberCommand.objects.filter(
                state=models.command.TO_BE_BANKED_STATE,
                payment_type=models.command.CHECK_PAYMENT,
            )
        )

        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance.bank_deposit,
        )
        return sum(cmd.amount for cmd in commands)


class CashBankDepositAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__', 'amount']
    form = forms.money_stock.CashBankDepositAdminForm
 
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        extra_context['current_treasury'] = models.money_stock.get_treasury()
        extra_context['sold_cash_cmd_total_amount'] = sum(cmd.price
            for cmd in models.MemberCommand.objects.filter(
                state=models.command.TO_BE_BANKED_STATE,
                payment_type=models.command.CASH_PAYMENT,
            )
        )
        extra_context['total_available_cash_amount'] = (extra_context['current_treasury'] +
                                                        extra_context['sold_cash_cmd_total_amount'])

        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance.bank_deposit,
        )
        treasury_ops = models.TreasuryOperation.objects.filter(
            bank_deposit=instance
        )
        return (sum(cmd.amount for cmd in commands) -
                sum(op.delta for op in treasury_ops))


class TreasuryOperationAdmin(admin.ModelAdmin):
    list_display = ['delta', 'reason',]
    form = forms.money_stock.TreasuryOperationAdminForm
    fields = forms.money_stock.TreasuryOperationAdminForm.Meta.fields

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


admin_site.register(models.BankDeposit, BankDepositAdmin)
admin_site.register(models.CheckBankDeposit, CheckBankDepositAdmin)
admin_site.register(models.CashBankDeposit, CashBankDepositAdmin)
admin_site.register(models.TreasuryOperation, TreasuryOperationAdmin)
