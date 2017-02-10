from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .command import *
from .configuration import get_config
from .individual_command import IndividualCommand
from . import user
from . import voucher

from .. import utils


class CommissionCommand(IndividualCommand):
    VOUCHER_COMMAND_TYPE = voucher.VoucherOperation.COMMISSION_COMMAND
    REASON_MAX_LEN = 250

    STATE_CHOICES = (
        (PLACED_STATE, 'Passée'),
        (TO_BE_PREPARED_STATE, 'À préparer'),
        (PREPARED_STATE, 'Préparée'),
        (GIVEN_STATE, 'Distribuée'),
        (CANCELLED_STATE, 'Annulée'),
    )

    commission = models.ForeignKey(
        user.Commission,
        related_name='commands',
        on_delete=models.CASCADE,
    )
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )
    datetime_given = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=REASON_MAX_LEN)

    class Meta:
        verbose_name = 'Commande commission'
        verbose_name_plural = 'Commandes commissions'

    def __str__(self):
        return '{} ({})'.format(
            self.id,
            self.commission.user.username,
        )

    @property
    def email(self):
        return self.commission.user.email

    @property
    def price(self):
        return 0

    @property
    def discount(self):
        return get_config().vip_percentage_discount / 100

    def distribute(self):
        if self.state != PREPARED_STATE:
            raise InvalidState()

        self.state = GIVEN_STATE
        self.datetime_given = now()
        self.save()

        send_mail(
            utils.format_mail_subject('Commande commission n°{} distribuée'.format(
                self.id,
            )),
            render_to_string(
                'bvc/mails/distribute_commission_command.txt',
                {
                    'amount': self.amount,
                    'commission': self.commission.user.username,
                    'reason': self.reason,
                }
            ),
            get_config().bvc_manager_mail,
            [get_config().treasurer_mail],
        )
