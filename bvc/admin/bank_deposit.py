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

    def amount(self, instance):
        raise NotImplementedError()

    date.admin_order_field = 'bank_deposit__date'
    ref.admin_order_field = 'bank_deposit__ref'
    made.admin_order_field = 'bank_deposit__made'
    made.boolean = True
    amount.short_description = 'Montant déposé'

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

    def get_readonly_fields(self, request, instance=None):
        if instance: # Editing an existing object
            if instance.bank_deposit.made:
                return list(self.readonly_fields) + ['bank_deposit']

        return list(self.readonly_fields) or []


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
        extra_context['numero'] = models.CheckBankDeposit.next_id()

        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        commands = models.CheckBankDeposit.objects.get(id=object_id).bank_deposit.commands.all()

        extra_context = extra_context or {}
        extra_context['commands'] = commands

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance.bank_deposit,
        )
        return sum(cmd.price for cmd in commands)

    amount.short_description = 'Montant déposé'

    def get_readonly_fields(self, request, instance=None):
        readonly_fields = super().get_readonly_fields(request, instance=instance)

        if instance:
            return readonly_fields + ['amount']
        return readonly_fields


class CashBankDepositAdmin(AbstractBankDepositAdmin):
    form = forms.bank_deposit.CashBankDepositAdminForm
    readonly_fields = ['treasury_operation',]

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
        extra_context['numero'] = models.CashBankDeposit.next_id()

        return super().add_view(request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        commands = models.CashBankDeposit.objects.get(id=object_id).bank_deposit.commands.all()

        extra_context = extra_context or {}
        extra_context['commands'] = commands
        extra_context['total_price'] = sum(c.price for c in commands)

        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def amount(self, instance):
        commands = models.MemberCommand.objects.filter(
            bank_deposit=instance.bank_deposit,
        )
        treasury_ops = models.TreasuryOperation.objects.filter(
            bank_deposit=instance
        )
        return (sum(cmd.price for cmd in commands) -
                sum(op.delta for op in treasury_ops))

    amount.short_description = 'Montant déposé'

    def get_readonly_fields(self, request, instance=None):
        readonly_fields = super().get_readonly_fields(request, instance=instance)

        if instance:
            if instance.treasury_operation:
                return readonly_fields + ['amount']
        return readonly_fields


admin_site.register(models.BankDeposit, BankDepositAdmin)
admin_site.register(models.CheckBankDeposit, CheckBankDepositAdmin)
admin_site.register(models.CashBankDeposit, CashBankDepositAdmin)
