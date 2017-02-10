import io
import csv
from itertools import chain

from django.db import models
from django.core.mail import send_mail, EmailMessage
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.conf import settings

from .command import *
from .configuration import get_config
from .individual_command import get_voucher_distribution
from .member_command import MemberCommand
from .commission_command import CommissionCommand
from . import validators
from . import voucher
from .. import utils


def get_current():
    try:
        return GroupedCommand.objects.exclude(state=PREPARED_STATE).first()
    except ObjectDoesNotExist:
        return None


def get_last():
    try:
        return GroupedCommand.objects.filter(state=PREPARED_STATE).last()
    except ObjectDoesNotExist:
        return None


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
        validators=[validators.validate_voucher_amount_multiple],
        verbose_name='Montant commandé',
    ) 
    received_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
        verbose_name='Montant reçu',
    )
    # Can be different from received_amount in case of loss
    prepared_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
        verbose_name='Montant préparé',
    )
    datetime_placed = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Date de commande',
    )
    datetime_received = models.DateField(
        null=True, blank=True,
        verbose_name='Date de réception',
    )
    datetime_prepared = models.DateField(
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
        dt = '-' if self.datetime_placed is None else self.datetime_placed.strftime('%d/%m/%Y')
        return '{} euros le {}'.format(
            self.placed_amount,
            dt,
        )
    
    def place(self, amount, datetime=None):
        if self.datetime_placed != None:
            raise InvalidState()

        self.placed_amount = amount
        self.datetime_placed = datetime or now()
        self.save()

        # Change the state of placed commands
        MemberCommand.objects.filter(state=PLACED_STATE).update(state=TO_BE_PREPARED_STATE)
        CommissionCommand.objects.filter(state=PLACED_STATE).update(state=TO_BE_PREPARED_STATE)

        # List distributed commission commands
        last_cmd = get_last()

        if last_cmd is None:
            distributed_commission_cmd = CommissionCommand.objects.filter(state=GIVEN_STATE)
        else:
            distributed_commission_cmd = CommissionCommand.objects.filter(
                state=GIVEN_STATE,
                datetime_given__gt=last_cmd.datetime_placed,
            )

        distributed_commission_cmd = list(distributed_commission_cmd) 

        if len(distributed_commission_cmd):
            csvfile = io.StringIO()
            total = 0
            writer = csv.writer(csvfile)
            writer.writerow(['Commission', 'Date', 'Raison', 'Bons',])
            for cmd in distributed_commission_cmd: 
                total += cmd.amount
                writer.writerow([cmd.commission.user.username, cmd.datetime_given.date(),
                                 cmd.reason, cmd.amount,])
            writer.writerow([])
            writer.writerow(['', '', 'Total', total,])
        
        mail_context = {
            'amount': amount,
            'commission_cmd': CommissionCommand.objects.filter(state=TO_BE_PREPARED_STATE), 
            'has_distributed_commission_cmd': len(distributed_commission_cmd),
        }

        if amount <= 0:
            self.receive(0, self.datetime_placed)
            self.prepare_(0, self.datetime_placed)

            email = EmailMessage(
                utils.format_mail_subject('Commande groupée n°{} non nécessaire'.format(self.id)),
                render_to_string('bvc/mails/no_grouped_command.txt', mail_context),
                get_config().bvc_manager_mail,
                [get_config().treasurer_mail],
                [],
            )
            if len(distributed_commission_cmd):
                email.attach(
                    'commandes_commissions_{}.csv'.format(1 if last_cmd is None else last_cmd.id), 
                    csvfile.getvalue(),
                    'text/csv'
                )
            email.send()
            return

        # Determine the quantity of each type of voucher
        placed_member_cmd = MemberCommand.objects.filter(state=TO_BE_PREPARED_STATE)
        placed_commission_cmd = CommissionCommand.objects.filter(state=TO_BE_PREPARED_STATE)
        cmd_amount = (MemberCommand.get_total_amount([TO_BE_PREPARED_STATE]) +
                      CommissionCommand.get_total_amount([TO_BE_PREPARED_STATE]))
        voucher_distribution = get_voucher_distribution(amount - cmd_amount)

        for cmd in chain(placed_member_cmd, placed_commission_cmd):
            for k in voucher_distribution:
                voucher_distribution[k] += cmd.voucher_distribution[k]
        mail_context['voucher_distribution'] = voucher_distribution

        # Send the email to the treasurer
        email = EmailMessage(
            utils.format_mail_subject('Commande groupée n°{}'.format(self.id)),
            render_to_string('bvc/mails/place_grouped_command.txt', mail_context),
            get_config().bvc_manager_mail,
            [get_config().treasurer_mail],
        )
        if len(distributed_commission_cmd):
            email.attach(
                'commandes_commissions_{}.csv'.format(1 if last_cmd is None else last_cmd.id), 
                csvfile.getvalue(),
                'text/csv'
            )
        email.send()

    def receive(self, amount, date):
        if self.state != PLACED_STATE:
            raise InvalidState()

        self.state = RECEIVED_STATE
        self.datetime_received = date
        self.received_amount = amount
        
        if amount > 0:
            send_mail(
                utils.format_mail_subject('Réception de commande groupée n°{}'.format(self.id)),
                render_to_string(
                    'bvc/mails/receive_grouped_command.txt',
                    {'command': self}
                ),
                get_config().treasurer_mail,
                [get_config().bvc_manager_mail],
            )

    def prepare_(self, amount, date):
        if self.state != RECEIVED_STATE:
            raise InvalidState()

        self.state = PREPARED_STATE
        self.datetime_prepared = date
        self.prepared_amount = amount

        voucher.update_stock(voucher.VoucherOperation.GROUPED_COMMAND, self.id, amount)        
        
        commission_commands = CommissionCommand.objects.filter(
            state=TO_BE_PREPARED_STATE,
        ).order_by('datetime_placed')
        member_commands = MemberCommand.objects.filter(
            state=TO_BE_PREPARED_STATE,
        ).order_by('datetime_placed')

        for cmd in chain(commission_commands, member_commands):
            # Not enough vouchers to prepare current command
            if voucher.get_stock() - cmd.amount < 0:
                send_mail(
                    utils.format_mail_subject('Commande indisponible'),
                    render_to_string(
                        'bvc/mails/command_unprepared.txt',
                        {'command': cmd,}
                    ),
                    get_config().bvc_manager_mail,
                    [cmd.email],
                )

                # Try to prepare smaller commands
                continue

            cmd.prepare()
