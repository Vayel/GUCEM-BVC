from django.contrib import admin

from .site import admin_site
from .. import models
from .. import forms


class GroupedCommandAdmin(admin.ModelAdmin):
    list_display = ['datetime_placed', 'placed_amount', 'received_amount',
                    'prepared_amount', 'state',]
    list_filter = ['state',]
    fields = forms.command.GroupedCommandAdminForm.Meta.fields
    form = forms.command.GroupedCommandAdminForm

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        # Remove delete action
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def get_readonly_fields(self, request, instance=None):
        if instance: # Editing an existing object
            fields = self.fields + []

            if instance.state is None:
                fields.remove('placed_amount')
                fields.remove('datetime_placed')
            elif instance.state == models.command.PLACED_STATE:
                fields.remove('received_amount')
                fields.remove('datetime_received')
            elif instance.state == models.command.RECEIVED_STATE:
                fields.remove('prepared_amount')
                fields.remove('datetime_prepared')

            return fields

        return self.readonly_fields or []

    def get_fields(self, request, instance=None):
        if instance: # Editing an existing object
            fields = self.fields

            if instance.datetime_placed is None:
                excluded = ['datetime_placed', 'received_amount',
                            'datetime_received', 'prepared_amount',
                            'datetime_prepared']
            elif instance.datetime_received is None:
                excluded = ['prepared_amount', 'datetime_prepared']
            else:
                excluded = []

            return [f for f in fields if f not in excluded]

        return self.fields or []


admin_site.register(models.GroupedCommand, GroupedCommandAdmin)
