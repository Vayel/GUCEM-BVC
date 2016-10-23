from itertools import chain

from django.db import models
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .command import *
from . import user
from . import validators
from . import money_stock
from . import voucher
from .. import utils


def cancel_old_commands():
    old_commands = MemberCommand.objects.filter(state=PREPARED_STATE)
    for cmd in old_commands:
        cmd.cancel()

def cash_commands():
    cmd = MemberCommand.objects.filter(
        state=SOLD_STATE,
        bank_deposit__isnull=False
    )

    cmd.update(state=CASHED_STATE)


class IndividualCommand(models.Model):
    """Represent a command placed to the manager."""
    amount = models.PositiveSmallIntegerField( # Amount before reduction
        default=0,
        validators=[validators.validate_amount_multiple],
    )
    comments = models.TextField(default='', blank=True,)
    datetime_placed = models.DateTimeField(auto_now_add=True,)
    datetime_prepared = models.DateTimeField(null=True, blank=True,)
    datetime_cancelled = models.DateTimeField(null=True, blank=True,)

    class Meta:
        abstract = True

    @property
    def price(self):
        return (1 - self.discount) * self.amount

    def prepare(self):
        if self.state != PLACED_STATE:
            raise InvalidState()

        self.state = PREPARED_STATE
        self.datetime_prepared = now()
        self.save()

        voucher.update_stock(self.VOUCHER_COMMAND_TYPE, self.id, -self.amount)        
        
        send_mail(
            utils.format_mail_subject('Commande reçue'),
            render_to_string(
                'bvc/mails/command_prepared.txt',
                {
                    'amount': self.amount,
                    'price': self.price,
                }
            ),
            settings.BVC_MANAGER_MAIL,
            [self.email],
        )

    def cancel(self):
        if self.state not in [PLACED_STATE, PREPARED_STATE]:
            raise InvalidState()

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
            settings.BVC_MANAGER_MAIL,
            [self.email],
        )


class MemberCommand(IndividualCommand):
    VOUCHER_COMMAND_TYPE = voucher.VoucherOperation.MEMBER_COMMAND
    
    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (PREPARED_STATE, 'Commande préparée'),
        (SOLD_STATE, 'Commande vendue'),
        (CASHED_STATE, 'Commande encaissée'),
        (CANCELLED_STATE, 'Commande annulée'),
    )

    CHECK_PAYMENT = 'check'
    CASH_PAYMENT = 'cash'

    PAYMENT_TYPE_CHOICES = (
        (CHECK_PAYMENT, 'Chèque'),
        (CASH_PAYMENT, 'Espèces'),
    )

    member = models.ForeignKey(user.Member, on_delete=models.CASCADE,)
    datetime_sold = models.DateTimeField(null=True, blank=True,)
    payment_type = models.CharField(
        null=True, blank=True,
        max_length=max(len(choice[0]) for choice in PAYMENT_TYPE_CHOICES),
        choices=PAYMENT_TYPE_CHOICES,
    )
    bank_deposit = models.ForeignKey(
        money_stock.BankDeposit,
        on_delete=models.CASCADE,
        null=True,
    )
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )
    
    class Meta:
        verbose_name = 'Commande adhérent'
        verbose_name_plural = 'Commandes adhérents'

    def __str__(self):
        return '{} ({} {})'.format(
            self.id,
            self.member.user.first_name,
            self.member.user.last_name,
        )

    @property
    def email(self):
        return self.member.user.email

    @property
    def discount(self):
        if self.member.vip:
            return settings.VIP_DISCOUNT
        elif self.member.club == user.Member.ESMUG:
            return settings.ESMUG_DISCOUNT
        elif self.member.club == user.Member.GUCEM: 
            return settings.GUCEM_DISCOUNT

        raise ValueError()

    def sell(self, payment_type):
        if self.state != PREPARED_STATE:
            raise InvalidState()

        self.state = SOLD_STATE
        self.datetime_sold = now()
        self.payment_type = payment_type
        self.save()

    def add_to_bank_deposit(self):
        if self.state != SOLD_STATE:
            raise InvalidState()

        self.bank_deposit = money_stock.get_current_bank_deposit()
        self.save()

    def remove_from_bank_deposit(self):
        if self.state != SOLD_STATE:
            raise InvalidState()

        self.bank_deposit = None
        self.save()

    def cash(self):
        if self.state != SOLD_STATE:
            raise InvalidState()

        self.state = CASHED_STATE
        self.datetime_cashed = now()
        self.save()


class CommissionCommand(IndividualCommand):
    VOUCHER_COMMAND_TYPE = voucher.VoucherOperation.COMMISSION_COMMAND

    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (PREPARED_STATE, 'Commande préparée'),
        (GIVEN_STATE, 'Commande distribuée'),
        (CANCELLED_STATE, 'Commande annulée'),
    )

    commission = models.ForeignKey(user.Commission, on_delete=models.CASCADE,)
    datetime_given = models.DateTimeField(null=True, blank=True)
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )
    
    class Meta:
        verbose_name = 'Commande commission'
        verbose_name_plural = 'Commandes commissions'

    def __str__(self):
        return '{} ({})'.format(
            self.id,
            self.commission.type,
        )

    @property
    def email(self):
        return self.commission.user.email

    @property
    def discount(self):
        return settings.VIP_DISCOUNT

    def distribute(self):
        if self.state != PREPARED_STATE:
            raise InvalidState()

        self.state = GIVEN_STATE
        self.datetime_given = now()
        self.save()
