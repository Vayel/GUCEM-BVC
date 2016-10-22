from itertools import chain

from django.db import models
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from . import user
from . import validators
from . import voucher
from .. import utils

# Common command states
PLACED_STATE = 'placed'
PREPARED_STATE = 'prepared'
CANCELLED_STATE = 'cancelled'
RECEIVED_STATE = 'received'
SOLD_STATE = 'sold'
CASHED_STATE = 'cashed'
GIVEN_STATE = 'given'



class InvalidState(Exception): pass

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

    @staticmethod
    def cancel_old_commands():
        old_commands = MemberCommand.objects.filter(state=PREPARED_STATE)
        for cmd in old_commands:
            cmd.cancel()

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
    VOUCHER_COMMAND_TYPE = voucher.Operation.MEMBER_COMMAND
    
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
    datetime_cashed = models.DateTimeField(null=True, blank=True,)
    payment_type = models.CharField(
        null=True, blank=True,
        max_length=max(len(choice[0]) for choice in PAYMENT_TYPE_CHOICES),
        choices=PAYMENT_TYPE_CHOICES,
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

    def cash(self):
        if self.state != SOLD_STATE:
            raise InvalidState()

        self.state = CASHED_STATE
        self.datetime_cashed = now()
        self.save()

class CommissionCommand(IndividualCommand):
    VOUCHER_COMMAND_TYPE = voucher.Operation.COMMISSION_COMMAND

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
