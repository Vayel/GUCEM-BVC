from smtplib import SMTPException

from django.contrib import admin, messages

from .site import admin_site
from .. import forms
from .. import models


class BankDepositAdmin(admin.ModelAdmin):
    form = forms.bank_deposit.BankDepositAdminForm

    def has_module_permission(self, request):
        return False


class AbstractBankDepositAdmin(admin.ModelAdmin):
    list_display = ['id', 'made', 'date', 'amount', 'ref',]
    actions = ['make',]
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def date(self, instance):
        return instance.bank_deposit.datetime

    def ref(self, instance):
        return instance.bank_deposit.ref

    def made(self, instance):
        return instance.bank_deposit.made

    date.admin_order_field = 'bank_deposit__date'
    ref.admin_order_field = 'bank_deposit__ref'
    made.admin_order_field = 'bank_deposit__made'
    made.boolean = True

    def make(self, request, queryset):
        for deposit in queryset:
            try:
                deposit.make()
            except models.bank_deposit.InvalidState:
                self.message_user(
                    request,
                    "Le dépôt {} n'est pas dans le bon état pour être déposé en banque.".format(deposit),
                    level=messages.ERROR
                )
            except SMTPException as e:
                self.message_user(
                    request,
                    "Une erreur est survenue en envoyant le mail : " + str(e),
                    level=messages.ERROR
                )


class CheckBankDepositAdmin(AbstractBankDepositAdmin):
    form = forms.bank_deposit.CheckBankDepositAdminForm

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
        return sum(cmd.price for cmd in commands)


class CashBankDepositAdmin(AbstractBankDepositAdmin):
    form = forms.bank_deposit.CashBankDepositAdminForm

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        extra_context['current_treasury'] = models.treasury.get_treasury()
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
        return (sum(cmd.price for cmd in commands) -
                sum(op.delta for op in treasury_ops))


admin_site.register(models.BankDeposit, BankDepositAdmin)
admin_site.register(models.CheckBankDeposit, CheckBankDepositAdmin)
admin_site.register(models.CashBankDeposit, CashBankDepositAdmin)
