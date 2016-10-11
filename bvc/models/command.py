from django.db import models

from . import user
from . import validators

# Common command states
PLACED_STATE = 'placed'
PREPARED_STATE = 'prepared'
CANCELLED_STATE = 'cancelled'

class GroupedCommand(models.Model):
    """Represent a command placed to the treasurer by the manager."""
    RECEIVED_STATE = 'received'

    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (RECEIVED_STATE, 'Commande disponible en magasin'),
        (PREPARED_STATE, 'Commande préparée'),
    )
    
    # Amounts in BVC value
    placed_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_amount_multiple],
    ) 
    received_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_amount_multiple],
    )
    # Can be different from received_amount in case of loss
    prepared_amount = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_amount_multiple],
    )
    datetime_placed = models.DateTimeField(auto_now_add=True,)
    datetime_received = models.DateTimeField(null=True, blank=True,)
    datetime_prepared = models.DateTimeField(null=True, blank=True,)
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )

    def __str__(self):
        return '{} euros (en Bons) le {}'.format(
            self.placed_amount,
            self.datetime_placed.strftime('%Y-%m-%d'),
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
    SOLD_STATE = 'sold'
    CASHED_STATE = 'cashed'

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
    GIVEN_STATE = 'given'

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
