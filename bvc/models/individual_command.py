from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .command import *
from .configuration import get_config
from . import validators
from . import voucher

from .. import utils

VOUCHER_SUBPACKET_AMOUNT = 500


def get_voucher_distribution(amount):
    if amount <= 0:
        return {10: 0, 20: 0, 50: 0,}
    elif amount <= 100:
        # Only 10
        return {10: amount // 10, 20: 0, 50: 0,}
    elif amount <= 200:
        # 10 * 10, the rest with 20 then 10
        default_10 = 10
        remaining = amount - 10 * default_10

        return {
            10: default_10 + (remaining % 20) // 10,
            20: remaining // 20,
            50: 0,
        }
    elif amount < VOUCHER_SUBPACKET_AMOUNT:
        # 10 * 10, 5 * 20, the rest with 50, 20 then 10
        default_10 = 10
        default_20 = 5
        remaining = amount - 10 * default_10 - 20 * default_20

        return {
            10: 10 + ((remaining % 50) % 20) // 10,
            20: 5 + (remaining % 50) // 20,
            50: remaining // 50,
        }
    else:
        subpacket_distrib = get_voucher_distribution(amount - VOUCHER_SUBPACKET_AMOUNT)
        subpacket_distrib[10] += 10
        subpacket_distrib[20] += 5
        subpacket_distrib[50] += 6

        return subpacket_distrib


def get_commands_voucher_distribution(commands):
    distribution = get_voucher_distribution(0)

    for cmd in commands:
        voucher.add_voucher_distribs(distribution, cmd.voucher_distribution)

    return distribution


class IndividualCommand(models.Model):
    """Represent a command placed to the manager."""
    amount = models.PositiveSmallIntegerField( # Amount before reduction
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
    )
    comments = models.TextField(default='', blank=True,)
    datetime_placed = models.DateTimeField(auto_now_add=True,)
    datetime_prepared = models.DateField(null=True, blank=True,)
    datetime_cancelled = models.DateField(null=True, blank=True,)

    class Meta:
        abstract = True

    @classmethod
    def get_total_amount(cls, states):
        total = cls.objects.filter(state__in=states).aggregate(models.Sum('amount'))['amount__sum']
        return total or 0

    @property
    def voucher_distribution(self):
        return get_voucher_distribution(self.amount)

    def prepare(self):
        if self.state != TO_BE_PREPARED_STATE:
            raise InvalidState("La commande {} n'est pas dans le bon état pour être préparée.".format(self))

        voucher.update_stock(self.VOUCHER_COMMAND_TYPE, self.id, -self.amount)        

        self.state = PREPARED_STATE
        self.datetime_prepared = now()
        self.save()

        send_mail(
            utils.format_mail_subject('Commande reçue'),
            render_to_string(
                'bvc/mails/command_prepared.txt',
                {
                    'amount': self.amount,
                    'price': self.price,
                }
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )

    def warn_about_cancellation(self):
        if self.state != PREPARED_STATE:
            raise InvalidState("La commande {} n'est pas dans le bon état pour être annulée.".format(self))

        send_mail(
            utils.format_mail_subject('Commande bientôt annulée'),
            render_to_string(
                'bvc/mails/cancel_command_soon.txt',
                {'cmd': self, 'grouped_command_day': get_config().grouped_command_day}
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )

    def cancel(self):
        if self.state not in [PLACED_STATE, TO_BE_PREPARED_STATE, PREPARED_STATE]:
            raise InvalidState("La commande {} n'est pas dans le bon état pour être annulée.".format(self))

        if self.state == PREPARED_STATE:
            voucher.update_stock(self.VOUCHER_COMMAND_TYPE, self.id, self.amount)

        self.state = CANCELLED_STATE
        self.datetime_cancelled = now()
        self.save()

        send_mail(
            utils.format_mail_subject('Commande annulée'),
            render_to_string(
                'bvc/mails/cancel_command.txt',
                {
                    'amount': self.amount,
                    'date': self.datetime_placed,
                }
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )

    def uncancel(self):
        if self.state not in [CANCELLED_STATE]:
            raise InvalidState("La commande {} n'est pas dans le bon état pour être désannulée.".format(self))

        self.state = PLACED_STATE
        datetime_cancelled = self.datetime_cancelled
        self.datetime_cancelled = None
        self.save()

        send_mail(
            utils.format_mail_subject('Commande désannulée'),
            render_to_string(
                'bvc/mails/uncancel_command.txt',
                {
                    'amount': self.amount,
                    'cancel_date': datetime_cancelled,
                }
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )
