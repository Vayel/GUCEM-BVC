from itertools import chain
from decimal import Decimal, getcontext

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
    return money_stock.get_treasury() + sum(cmd.price
        for cmd in MemberCommand.objects.filter(
            state=TO_BE_BANKED_STATE,
            payment_type=CASH_PAYMENT,
        )
    )

def get_voucher_distribution(amount):
    VOUCHER_SUBPACKET_AMOUNT = 500

    if amount >= VOUCHER_SUBPACKET_AMOUNT:
        subpacket_distrib = get_voucher_distribution(amount - VOUCHER_SUBPACKET_AMOUNT)
        subpacket_distrib[10] += 10
        subpacket_distrib[20] += 5
        subpacket_distrib[50] += 6
        return subpacket_distrib
    elif amount <= 100:
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
    else:
        # 10 * 10, 5 * 20, the rest with 50, 20 then 10
        default_10 = 10
        default_20 = 5
        remaining = amount - 10 * default_10 - 20 * default_20

        return {
            10: 10 + ((remaining % 50) % 20) // 10,
            20: 5 + (remaining % 50) // 20,
            50: remaining // 50, 
        }


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

    @property
    def price(self):
        return (Decimal('1') - Decimal(str(self.discount))) * Decimal(str(self.amount))

    @classmethod
    def get_total_amount(cls, states):
        total = cls.objects.filter(state__in=states).aggregate(models.Sum('amount'))['amount__sum']
        return total or 0

    @property
    def voucher_distribution(self):
        return get_voucher_distribution(self.amount)

    def prepare(self):
        if self.state != PLACED_STATE:
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
                    'paid_command': isinstance(self, MemberCommand),
                }
            ),
            settings.BVC_MANAGER_MAIL,
            [self.email],
        )

    def cancel(self):
        if self.state not in [PLACED_STATE, PREPARED_STATE]:
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
            settings.BVC_MANAGER_MAIL,
            [self.email],
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


class CommissionCommand(IndividualCommand):
    VOUCHER_COMMAND_TYPE = voucher.VoucherOperation.COMMISSION_COMMAND

    STATE_CHOICES = (
        (PLACED_STATE, 'Passée'),
        (TO_BE_PREPARED_STATE, 'À préparer'),
        (PREPARED_STATE, 'Préparée'),
        (GIVEN_STATE, 'Distribuée'),
        (CANCELLED_STATE, 'Annulée'),
    )

    commission = models.ForeignKey(user.Commission, related_name='commands', on_delete=models.CASCADE,)
    datetime_given = models.DateTimeField(null=True, blank=True)
    reason = models.TextField()
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
            self.commission.user.username,
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
