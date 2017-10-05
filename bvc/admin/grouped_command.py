from django.contrib import admin
from django.conf import settings

from .site import admin_site
from .. import models
from .. import forms


class GroupedCommandAdmin(admin.ModelAdmin):
    list_display = ['datetime_placed', 'placed_amount', 'received_amount',
                    'state',]
    list_filter = ['state',]
    fields = forms.grouped_command.GroupedCommandAdminForm.Meta.fields
    form = forms.grouped_command.GroupedCommandAdminForm

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return not models.GroupedCommand.objects.exclude(
            state=models.command.PREPARED_STATE
        ).count()

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
                fields.remove('datetime_prepared')

            return fields

        return self.readonly_fields or []

    def get_fields(self, request, instance=None):
        if instance: # Editing an existing object
            if instance.state == None:
                excluded = ['datetime_placed', 'received_amount', 'datetime_received',
                            'datetime_prepared']
            elif instance.state == models.command.PLACED_STATE:
                excluded = ['datetime_prepared']
            else:
                excluded = []
        else:
            excluded = ['state', 'datetime_placed', 'received_amount',
                        'datetime_received', 'datetime_prepared']

        return [f for f in self.fields or [] if f not in excluded]
    
    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        extra_context['unprepared_cmd_count'] = models.GroupedCommand.objects.exclude(
            state=models.command.PREPARED_STATE
        ).count()
        extra_context['being_sold_cmd_number'] = (models.MemberCommand.objects.filter(
                                                     state=models.command.PREPARED_STATE
                                                 ).count() +
                                                 models.CommissionCommand.objects.filter(
                                                     state=models.command.PREPARED_STATE
                                                 ).count())
        extra_context['amount_being_sold'] = (models.MemberCommand.get_total_amount(
                                                  [models.command.PREPARED_STATE]
                                              ) + 
                                              models.CommissionCommand.get_total_amount(
                                                  [models.command.PREPARED_STATE]))

        extra_context['placed_by_members'] = models.MemberCommand.get_total_amount(
            [models.command.PLACED_STATE]
        )
        extra_context['placed_by_commissions'] = models.CommissionCommand.get_total_amount(
            [models.command.PLACED_STATE]
        )
        extra_context['placed_amount'] = (extra_context['placed_by_members'] +
                                          extra_context['placed_by_commissions'])
        extra_context['remaining'] = models.voucher.get_stock()
        extra_context['min_to_place'] = models.grouped_command.min_amount_to_place()

        extra_context['extra_amount'] = models.get_config().grouped_command_extra_amount
        extra_context['recommended_to_place'] = models.grouped_command.min_amount_to_place(extra_context['extra_amount'])

        return super().add_view(request, form_url=form_url, extra_context=extra_context)


admin_site.register(models.GroupedCommand, GroupedCommandAdmin)
