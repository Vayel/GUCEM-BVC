from django.db import models

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
        return '{} euros le {}'.format(
            self.placed_amount,
            self.datetime_placed.strftime('%Y-%m-%d'),
        )

class IndividualCommand(models.Model):
    """Represent a command placed to the manager."""
    grouped_command = models.ForeignKey(
        GroupedCommand,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    amount = models.PositiveSmallIntegerField(default=0,)
    email = models.EmailField()
    comments = models.TextField(default='', blank=True,)
    datetime_placed = models.DateTimeField(auto_now_add=True,)
    datetime_prepared = models.DateTimeField(null=True, blank=True,)
    datetime_cancelled = models.DateTimeField(null=True, blank=True,)

    class Meta:
        abstract = True
    
    def __str__(self):
        return '{} euros le {} pour {}'.format(
            self.amount,
            self.datetime_placed.strftime('%Y-%m-%d'),
            self.email,
        )
    
class MemberCommand(IndividualCommand):
    ESMUG = 'esmug'
    GUCEM = 'gucem'

    SOLD_STATE = 'sold'
    CASHED_STATE = 'cashed'

    CLUB_CHOICES = (
        (GUCEM, 'GUCEM'),
        (ESMUG, 'ESMUG'),
    )

    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (PREPARED_STATE, 'Commande préparée'),
        (SOLD_STATE, 'Commande vendue'),
        (CASHED_STATE, 'Commande encaissée'),
        (CANCELLED_STATE, 'Commande annulée'),
    )

    lastname = models.CharField(max_length=30,)
    firstname = models.CharField(max_length=30,)
    license = models.CharField(max_length=12,)
    datetime_sold = models.DateTimeField(null=True, blank=True,)
    datetime_cashed = models.DateTimeField(null=True, blank=True,)
    
    club = models.CharField(
        max_length=max(len(choice[0]) for choice in CLUB_CHOICES),
        choices=CLUB_CHOICES,
        default=GUCEM,
    )
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )

class CommissionCommand(IndividualCommand):
    CANYONING = 'canyoning'
    CLIMBING = 'climbing'
    CAVING = 'caving'
    MOUNTAINEERING = 'mountaineering'

    PLACED_STATE = 'placed'
    PREPARED_STATE = 'prepared'
    GIVEN_STATE = 'given'

    COMMISSION_CHOICES = (
        (CANYONING, 'Canyoning'),
        (CLIMBING, 'Escalade'),
        (CAVING, 'Spéléologie'),
        (MOUNTAINEERING, 'Alpinisme'),
    )

    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (PREPARED_STATE, 'Commande préparée'),
        (GIVEN_STATE, 'Commande distribuée'),
        (CANCELLED_STATE, 'Commande annulée'),
    )

    datetime_given = models.DateTimeField(null=True, blank=True)
    commission = models.CharField(
        max_length=max(len(choice[0]) for choice in COMMISSION_CHOICES),
        choices=COMMISSION_CHOICES,
        default=CANYONING,
    )
    state = models.CharField(
        max_length=max(len(choice[0]) for choice in STATE_CHOICES),
        choices=STATE_CHOICES,
        default=PLACED_STATE,
    )
