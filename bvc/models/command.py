from django.db import models

# common command states
PLACED_STATE = 'placed'
PREPARED_STATE = 'prepared'
CANCELLED_STATE = 'cancelled'

class AbstractCommand(models.Model):
    amount = models.PositiveSmallIntegerField(default=0)
    email = models.EmailField()
    comments = models.TextField(default='')
    datetime_placed = models.DateTimeField(auto_now_add=True)
    datetime_prepared = models.DateTimeField()
    datetime_cancelled = models.DateTimeField()
    class Meta:
        abstract = True
    
class MemberCommand(AbstractCommand):
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
    datetime_sold = models.DateTimeField()
    datetime_cashed = models.DateTimeField()
    
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

class CommissionCommand(AbstractCommand):
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

    datetime_given = models.DateTimeField()
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
