from django.db import models
from django.utils.timezone import now
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from . import user
from . import validators
from .. import utils

# Common command states
PLACED_STATE = 'placed'
PREPARED_STATE = 'prepared'
CANCELLED_STATE = 'cancelled'
RECEIVED_STATE = 'received'
SOLD_STATE = 'sold'
CASHED_STATE = 'cashed'
GIVEN_STATE = 'given'

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
        auto_now_add=True,
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

    def __str__(self):
        return '{} euros le {}'.format(
            self.placed_amount,
            self.datetime_placed.strftime('%d/%m/%Y'),
        )

    def receive(self, amount):
        if amount > self.placed_amount:
            raise ValueError('')

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
    
class MemberCommand(IndividualCommand):
    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (PREPARED_STATE, 'Commande préparée'),
        (SOLD_STATE, 'Commande vendue'),
        (CASHED_STATE, 'Commande encaissée'),
        (CANCELLED_STATE, 'Commande annulée'),
    )

    member = models.ForeignKey(user.Member, on_delete=models.CASCADE,)
    datetime_sold = models.DateTimeField(null=True, blank=True,)
    datetime_cashed = models.DateTimeField(null=True, blank=True,)
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )
    
    def __str__(self):
        return '{}\n{}'.format(
            super(MemberCommand, self).__str__(),
            self.member.user.first_name,
            self.member.user.last_name,
        )

class CommissionCommand(IndividualCommand):
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
    
    def __str__(self):
        return '{}\nCommission : {}\nEtat : {}\nDistribuée le : {}\n'.format(
            super(CommissionCommand, self).__str__(),
            self.commission.type,
            self.state,
            self.datetime_given.strftime('%Y-%m-%d'),
        )
