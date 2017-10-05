from django.contrib import admin

from .site import admin_site
from .. import forms
from .. import models


class TreasuryOperationAdmin(admin.ModelAdmin):
    list_display = ['id', 'stock', 'delta', 'date', 'reason',]
    list_display_links = None
    list_editable = ['reason',]
    form = forms.treasury.TreasuryOperationAdminForm
    fields = forms.treasury.TreasuryOperationAdminForm.Meta.fields

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['treasury'] = models.treasury.get_treasury()

        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['treasury'] = models.treasury.get_treasury()

        return super().add_view(request, form_url=form_url, extra_context=extra_context)


admin_site.register(models.TreasuryOperation, TreasuryOperationAdmin)
