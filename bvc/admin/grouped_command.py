import smtplib

from django.contrib import admin, messages
from django.utils.timezone import now
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .. import models
from .. import forms


@admin.register(models.command.GroupedCommand)
class GroupedCommandAdmin(admin.ModelAdmin):
    list_display = ['datetime_placed', 'placed_amount', 'received_amount',
                    'prepared_amount', 'state',]
    list_filter = ['state',]
    fields = forms.command.GroupedCommandAdmin.Meta.fields
    form = forms.command.GroupedCommandAdmin

    def get_readonly_fields(self, request, instance=None):
        if instance: # Editing an existing object
            fields = self.fields + []

            if instance.datetime_placed is None:
                fields.remove('placed_amount')
            elif instance.datetime_received is None:
                fields.remove('received_amount')
            elif instance.datetime_prepared is None:
                fields.remove('prepared_amount')

            return fields

        return self.readonly_fields or []

    def get_fields(self, request, instance=None):
        if instance: # Editing an existing object
            fields = self.fields

            if instance.datetime_placed is None:
                excluded = ['datetime_placed', 'received_amount',
                            'datetime_received', 'prepared_amount',
                            'datetime_prepared']
                fields = [f for f in fields if f not in excluded]
            elif instance.datetime_received is None:
                excluded = ['datetime_received', 'prepared_amount',
                            'datetime_prepared']
                fields = [f for f in fields if f not in excluded]
            elif instance.datetime_prepared is None:
                excluded = ['datetime_prepared']
                fields = [f for f in fields if f not in excluded]

            return fields

        return self.fields or []
