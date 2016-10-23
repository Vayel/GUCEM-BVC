from django.contrib import admin

from .. import forms
from .. import models

@admin.register(models.BankDeposit)
class BankDepositAdmin(admin.ModelAdmin):
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
