import io
import csv
from itertools import chain

from django.db import models
from django.core.mail import send_mail, EmailMessage
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from .command import *
from .configuration import get_config
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


def get_last_prepared():
    try:
        return GroupedCommand.objects.filter(state=PREPARED_STATE).last()
    except ObjectDoesNotExist:
        return None


def get_cancelled_cmd_after_date(datetime=None):
    member_cmd = MemberCommand.objects.filter(
        state=CANCELLED_STATE,
    )
    commission_cmd = CommissionCommand.objects.filter(
        state=CANCELLED_STATE,
    )

    if datetime is not None:
        member_cmd = member_cmd.filter(datetime_cancelled__gt=datetime)
        commission_cmd = commission_cmd.filter(datetime_cancelled__gt=datetime)

    return chain(member_cmd, commission_cmd)


def min_amount_to_place(margin=0):
    return max(0, MemberCommand.get_total_amount([PLACED_STATE, TO_BE_PREPARED_STATE]) +
               CommissionCommand.get_total_amount([PLACED_STATE, TO_BE_PREPARED_STATE]) -
               voucher.get_stock() + margin)


class GroupedCommand(models.Model):
    """Represent a command placed to the treasurer by the manager."""
    STATE_CHOICES = (
        (PLACED_STATE, 'Passée au trésorier'),
        (RECEIVED_STATE, 'Disponible en magasin'),
        (PREPARED_STATE, 'Préparée'),
    )

    # Amounts in BVC value
    placed_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
        verbose_name='montant commandé',
    )
    received_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
        verbose_name='montant reçu',
    )
    datetime_placed = models.DateTimeField(
        null=True, blank=True,
        verbose_name='date de commande',
    )
    datetime_received = models.DateField(
        null=True, blank=True,
        verbose_name='date de réception',
    )
    datetime_prepared = models.DateField(
        null=True, blank=True,
        verbose_name='date de préparation',
    )
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
        verbose_name='état',
    )

    class Meta:
        verbose_name = 'Commande groupée'
        verbose_name_plural = 'Commandes groupées'

    def __str__(self):
        return 'Commande groupée {} (id {})'.format(
            self.datetime_placed.strftime('%Y-%m-%d'),
            self.id,
        )

    def voucher_distrib_to_place(self):
        """Determine the quantity of each type of voucher. We should have the correct
        distribution for every command, but maybe some vouchers are taken from
        cancelled commands, so we cannot choose their type.
        """

        amount = self.placed_amount

        member_cmd = MemberCommand.objects.filter(state=TO_BE_PREPARED_STATE)
        commission_cmd = CommissionCommand.objects.filter(state=TO_BE_PREPARED_STATE)
        cmd_voucher_distrib = voucher.get_commands_distrib(
            chain(member_cmd, commission_cmd)
        )

        # First, we reuse old vouchers, i.e. from cancelled commands
        previous_cmd = get_last_prepared()
        cancelled_cmd_voucher_distrib = voucher.get_commands_distrib(
            get_cancelled_cmd_after_date(
                None if previous_cmd is None else previous_cmd.datetime_prepared
            )
        )

        for k, v in cancelled_cmd_voucher_distrib.items():
            cmd_voucher_distrib[k] = max(0, cmd_voucher_distrib[k] - v)

        # cmd_voucher_distrib is now the number of vouchers of each type missing
        # i.e. the ones we need to order. But maybe the command is not big enough to
        # buy them all, so we start with lower vouchers because we do not want
        # to lack them afterwards.

        voucher_distrib = voucher.get_distrib(0)

        for voucher_value, voucher_number in sorted(cmd_voucher_distrib.items()):
            for _ in range(voucher_number):
                if amount - voucher_value < 0:
                    break

                amount -= voucher_value
                voucher_distrib[voucher_value] += 1

        # amount is now the amount remaning to place

        voucher.add_distribs(voucher_distrib, voucher.get_distrib(amount))

        return voucher_distrib

    def place(self, amount, datetime=None):
        if self.datetime_placed != None:
            raise InvalidState()

        self.placed_amount = amount
        self.datetime_placed = datetime or now()
        self.save()

        email = EmailMessage(
            '',
            '',
            get_config().bvc_manager_mail,
            [get_config().treasurer_mail],
            [],
        )

        # Change the state of placed commands
        MemberCommand.objects.filter(state=PLACED_STATE).update(state=TO_BE_PREPARED_STATE)
        CommissionCommand.objects.filter(state=PLACED_STATE).update(state=TO_BE_PREPARED_STATE)

        # List distributed commission commands
        previous_cmd = get_last_prepared()

        if previous_cmd is None:
            distributed_commission_cmd = CommissionCommand.objects.filter(state=GIVEN_STATE)
        else:
            distributed_commission_cmd = CommissionCommand.objects.filter(
                state=GIVEN_STATE,
                datetime_given__gt=previous_cmd.datetime_placed,
            )

        distributed_commission_cmd = list(distributed_commission_cmd)

        if len(distributed_commission_cmd):
            csvfile = io.StringIO()
            total = 0
            writer = csv.writer(csvfile)
            writer.writerow(['Id', 'Commission', 'Date de commande',
                             'Date de distribution', 'Raison', 'Bons',])
            for cmd in distributed_commission_cmd:
                total += cmd.amount
                writer.writerow([cmd.id, cmd.commission.user.username,
                                 cmd.datetime_placed.date(), cmd.datetime_given.date(),
                                 cmd.reason, cmd.amount,])
            writer.writerow([])
            writer.writerow(['', '', '', '', 'Total', total,])

            email.attach(
                'commandes_commissions_{}.csv'.format(
                    1 if previous_cmd is None else previous_cmd.id
                ),
                csvfile.getvalue(),
                'text/csv'
            )

        # Send mail to treasurer
        mail_context = {
            'amount': amount,
            'commission_cmd': CommissionCommand.objects.filter(state=TO_BE_PREPARED_STATE), 
            'has_distributed_commission_cmd': len(distributed_commission_cmd),
            'voucher_distribution': self.voucher_distrib_to_place(),
        }

        if amount <= 0:
            self.receive(0, self.datetime_placed)
            self.prepare_(0, self.datetime_placed)

            email.subject = utils.format_mail_subject(
                '{} non nécessaire'.format(str(self))
            )
            email.body = render_to_string('bvc/mails/no_grouped_command.txt', mail_context)
        else:
            email.subject = utils.format_mail_subject(str(self))
            email.body = render_to_string('bvc/mails/place_grouped_command.txt', mail_context)

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

        voucher.update_stock(amount, str(self))

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
