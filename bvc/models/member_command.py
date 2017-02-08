from decimal import Decimal, getcontext

from django.db import models
from django.conf import settings
from django.utils.timezone import now

from .command import *
from .individual_command import IndividualCommand
from . import bank_deposit
from . import treasury
from . import user
from . import voucher

getcontext().prec = 6


def cancel_old_commands():
    old_commands = MemberCommand.objects.filter(state=PREPARED_STATE)
    for cmd in old_commands:
        cmd.cancel()


def bank_commands(payment_type, bank_deposit):
    commands = MemberCommand.objects.filter(
        state=TO_BE_BANKED_STATE,
        payment_type=payment_type,
    )

    for cmd in commands:
        cmd.bank(bank_deposit)


def get_available_cash_amount():
    return treasury.get_treasury() + sum(cmd.price
        for cmd in MemberCommand.objects.filter(
            state=TO_BE_BANKED_STATE,
            payment_type=CASH_PAYMENT,
        )
    )


class MemberCommand(IndividualCommand):
    VOUCHER_COMMAND_TYPE = voucher.VoucherOperation.MEMBER_COMMAND
    
    STATE_CHOICES = (
        (PLACED_STATE, 'Passée'),
        (TO_BE_PREPARED_STATE, 'À préparer'),
        (PREPARED_STATE, 'Préparée'),
        (SOLD_STATE, 'Vendue'),
        (TO_BE_BANKED_STATE, 'À encaisser'),
        (BANKED_STATE, 'Encaissée'),
        (CANCELLED_STATE, 'Annulée'),
    )

    PAYMENT_TYPE_CHOICES = (
        (CHECK_PAYMENT, 'Chèque'),
        (CASH_PAYMENT, 'Espèces'),
    )

    AUTO_BANKED_PAYMENT_TYPES = [CASH_PAYMENT]

    member = models.ForeignKey(user.Member, related_name='commands', on_delete=models.CASCADE,)
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )
    datetime_sold = models.DateTimeField(null=True, blank=True,)
    payment_type = models.CharField(
        null=True, blank=True,
        max_length=max(len(choice[0]) for choice in PAYMENT_TYPE_CHOICES),
        choices=PAYMENT_TYPE_CHOICES,
    )
    bank_deposit = models.ForeignKey(
        bank_deposit.BankDeposit,
        on_delete=models.CASCADE,
        null=True,
        related_name='commands',
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
    def price(self):
        return (Decimal('1') - Decimal(str(self.discount))) * Decimal(str(self.amount))

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

        self.state = TO_BE_BANKED_STATE if payment_type in self.AUTO_BANKED_PAYMENT_TYPES else SOLD_STATE
        self.datetime_sold = now()
        self.payment_type = payment_type
        self.save()

    def add_for_bank_deposit(self):
        if self.state != SOLD_STATE:
            raise InvalidState()

        self.state = TO_BE_BANKED_STATE
        self.save()

    def remove_from_bank_deposit(self):
        if self.state != TO_BE_BANKED_STATE:
            raise InvalidState()
        if self.payment_type in self.AUTO_BANKED_PAYMENT_TYPES:
            raise InvalidPaymentType()

        self.state = SOLD_STATE
        self.save()

    def bank(self, bank_deposit):
        if self.state != TO_BE_BANKED_STATE:
            raise InvalidState()

        self.state = BANKED_STATE
        self.bank_deposit = bank_deposit
        self.save()
