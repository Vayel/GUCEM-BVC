from itertools import chain

from django.db import models
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .command import *
from . import user
from . import validators
from . import voucher
from .. import utils

class GroupedCommand(models.Model):
    """Represent a command placed to the treasurer by the manager."""
    STATE_CHOICES = (
        (PLACED_STATE, 'Commande passée au trésorier'),
        (RECEIVED_STATE, 'Commande disponible en magasin'),
        (PREPARED_STATE, 'Commande préparée'),
    )
    
    # Amounts in BVC value
    placed_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_amount_multiple],
        verbose_name='Montant commandé',
    ) 
    received_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_amount_multiple],
        verbose_name='Montant reçu',
    )
    # Can be different from received_amount in case of loss
    prepared_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_amount_multiple],
        verbose_name='Montant préparé',
    )
    datetime_placed = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Date de commande',
    )
    datetime_received = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Date de réception',
    )
    datetime_prepared = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Date de préparation',
    )
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
        verbose_name='Etat',
    )

    class Meta:
        verbose_name = 'Commande groupée'
        verbose_name_plural = 'Commandes groupées'

    def __str__(self):
        return '{} euros le {}'.format(
            self.placed_amount,
            self.datetime_placed.strftime('%d/%m/%Y'),
        )
    
    @staticmethod
    def get_amount_to_place():
        commission_commands = CommissionCommand.objects.filter(
            state=PLACED_STATE,
        ).order_by('datetime_placed')
        member_commands = MemberCommand.objects.filter(
            state=PLACED_STATE,
        ).order_by('datetime_placed')

        return (
            sum(cmd.amount for cmd in chain(commission_commands, member_commands)) +
            settings.VOUCHER_STOCK_MIN +
            settings.GROUPED_COMMAND_EXTRA_AMOUNT
        )
        
    def place(self, amount):
        if self.state != None:
            raise InvalidState()

        if amount <= 0:
            send_mail(
                utils.format_mail_subject('Commande groupée non nécessaire'),
                render_to_string('bvc/mails/no_grouped_command.txt',),
                settings.BVC_MANAGER_MAIL,
                [settings.TREASURER_MAIL],
            )
            return

        self.placed_amount = amount
        self.datetime_placed = now()
        self.save()

        send_mail(
            utils.format_mail_subject('Commande groupée'),
            render_to_string(
                'bvc/mails/place_grouped_command.txt',
                {'amount': amount}
            ),
            settings.BVC_MANAGER_MAIL,
            [settings.TREASURER_MAIL],
        )

    def receive(self, amount):
        if self.state != PLACED_STATE:
            raise InvalidState()

        self.state = RECEIVED_STATE
        self.datetime_received = now()
        self.received_amount = amount
        self.save()
        
        send_mail(
            utils.format_mail_subject('Réception de commande groupée'),
            render_to_string(
                'bvc/mails/receive_grouped_command.txt',
                {'command': self}
            ),
            settings.TREASURER_MAIL,
            [settings.BVC_MANAGER_MAIL],
        )

    def prepare_(self, amount):
        if self.state != PREPARED_STATE:
            raise InvalidState()

        self.state = PREPARED_STATE
        self.datetime_prepared = now()
        self.prepared_amount = amount
        self.save()

        voucher.update_stock(voucher.Operation.GROUPED_COMMAND, self.id, amount)        
        
        commission_commands = CommissionCommand.objects.filter(
            state=PLACED_STATE,
        ).order_by('datetime_placed')
        member_commands = MemberCommand.objects.filter(
            state=PLACED_STATE,
        ).order_by('datetime_placed')

        for cmd in chain(commission_commands, member_commands):
            # Not enough vouchers to prepare current command
            if voucher.get_stock() - cmd.amount < settings.VOUCHER_STOCK_MIN:
                send_mail(
                    utils.format_mail_subject('Commande indisponible'),
                    render_to_string(
                        'bvc/mails/command_unprepared.txt',
                        {'command': cmd,}
                    ),
                    settings.BVC_MANAGER_MAIL,
                    [cmd.email],
                )

                # Try to prepare smaller commands
                continue

            cmd.prepare()