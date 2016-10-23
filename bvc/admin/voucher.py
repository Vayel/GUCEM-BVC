from django.contrib import admin

from .. import models


@admin.register(models.VoucherOperation)
class OperationAdmin(admin.ModelAdmin):
    readonly_fields = ['command_type', 'command_id', 'stock',]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions
