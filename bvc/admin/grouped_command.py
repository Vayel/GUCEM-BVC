import smtplib

from django.contrib import admin, messages
from django.utils.timezone import now
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .. import models
from .. import utils


class CommandAdmin(admin.ModelAdmin):
    readonly_fields = ['datetime_placed']
    exclude = []


class GroupedCommandAdmin(CommandAdmin):
    list_display = ['datetime_placed', 'placed_amount', 'received_amount',
                    'prepared_amount', 'state',]
    fields = ['state', 'datetime_placed', 'placed_amount', 'datetime_received',
              'received_amount', 'datetime_prepared', 'prepared_amount',]
    list_filter = ['state',]
    actions = ['receive']

    def receive(self, request, queryset):
        if queryset.filter(~Q(state=models.command.PLACED_STATE)).count():
            self.message_user(
                request,
                'Une des commandes a déjà été reçue. Opération annulée.',
                level=messages.ERROR,
            )
            return

        queryset.update(
            state=models.command.RECEIVED_STATE,
            datetime_received=now(),
        )
        
        self.message_user(
            request,
            'Les commandes ont été mises à jour. Merci de renseigner le montant reçu pour chacune.',
            level=messages.SUCCESS,
        )

        try:
            send_mail(
                utils.format_mail_subject('Réception de commandes groupées'),
                render_to_string(
                    'bvc/mails/receive_grouped_command.txt',
                    {'commands': queryset}
                ),
                settings.TREASURER_MAIL,
                [settings.BVC_MANAGER_MAIL],
            )
        except smtplib.SMTPException:
            self.message_user(
                request,
                "Le mail n'a pas pu être envoyé au responsable des bons. Merci de le faire manuellement.",
                level=messages.WARNING,
            )



admin.site.register(models.command.GroupedCommand, GroupedCommandAdmin)
