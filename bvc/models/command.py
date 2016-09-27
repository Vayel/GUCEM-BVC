from django.db import models

from . import user

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
    placed_amount = models.PositiveSmallIntegerField(default=0,) 
    received_amount = models.PositiveSmallIntegerField(default=0,)
    # Can be different from received_amount in case of loss
    prepared_amount = models.PositiveSmallIntegerField(default=0,)
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
    # Set at preparation
    grouped_command = models.ForeignKey(
        GroupedCommand,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    amount = models.PositiveSmallIntegerField(default=0,) # amount in BVC value
    comments = models.TextField(default='', blank=True,)
    datetime_placed = models.DateTimeField(auto_now_add=True,)
    datetime_prepared = models.DateTimeField(null=True, blank=True,)
    datetime_cancelled = models.DateTimeField(null=True, blank=True,)

    class Meta:
        abstract = True
    
    def __str__(self):
        return '{} euros (en Bons) le {} pour {}'.format(
            self.amount,
            self.datetime_placed.strftime('%Y-%m-%d'),
            self.email,
        )
    
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
        return '{}\n{} {}\nClub : {}\nLic : {}\nEtat : {}\nVendue le : {}\nEncaissée le : {}'.format(
            super(MemberCommand, self).__str__(),
            self.firstname,
            self.lastname,
            self.club,
            self.license,
            self.state,
            self.datetime_sold.strftime('%Y-%m-%d'),
            self.datetime_cashed.strftime('%Y-%m-%d'),
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
            self.commission,
            self.state,
            self.datetime_given.strftime('%Y-%m-%d'),
        )
