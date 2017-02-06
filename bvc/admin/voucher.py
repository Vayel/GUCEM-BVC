from django.contrib import admin

from .site import admin_site
from .. import models


class VoucherOperationAdmin(admin.ModelAdmin):
    list_display = ['id', 'stock',]
    readonly_fields = ['command_type', 'command_id', 'stock',]

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['voucher_stock'] = models.voucher.get_stock()

        return super().changelist_view(request, extra_context=extra_context)


admin_site.register(models.VoucherOperation, VoucherOperationAdmin)
