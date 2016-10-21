import smtplib

from django.contrib import admin, messages
from django.utils.timezone import now
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .. import models
from .. import forms


"""
class CommandAdmin(admin.ModelAdmin):
    readonly_fields = ['datetime_placed']
    exclude = []
"""

@admin.register(models.command.GroupedCommand)
class GroupedCommandAdmin(admin.ModelAdmin):
    list_display = ['datetime_placed', 'placed_amount', 'received_amount',
                    'prepared_amount', 'state',]
    list_filter = ['state',]
    readonly_fields = ['state', 'datetime_placed', 'placed_amount', 'datetime_received',
              'received_amount', 'datetime_prepared', 'prepared_amount',]
    fields = readonly_fields + ['amount']

    form = forms.command.GroupedCommandAdmin
