from django.db import models

class AbstractCommand(models.Model):
    amout = models.PositiveSmallIntegerField(default=0)
    datetime = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    comments = models.TextField(default='')

class MemberCommand(AbstractCommand):
    ESMUG = 'esmug'
    GUCEM = 'gucem'

    PLACED_STATE = 'placed'
    PREPARED_STATE = 'prepared'
    SOLD_STATE = 'sold'
    CASHED_STATE = 'cashed'
    CANCELED_STATE = 'canceled'

    CLUB_CHOICES = (
        (GUCEM, 'GUCEM'),
        (ESMUG, 'ESMUG'),
    )

    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (PREPARED_STATE, 'Commande préparée'),
        (SOLD_STATE, 'Commande vendue'),
        (CASHED_STATE, 'Commande encaissée'),
        (CANCELED_STATE, 'Commande annulée'),
    )

    lastname = models.CharField(max_length=30,)
    firstname = models.CharField(max_length=30,)
    license = models.CharField(max_length=12,)
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
    SOLD_STATE = 'sold'

    COMMISSION_CHOICES = (
        (CANYONING, 'Canyoning'),
        (CLIMBING, 'Escalade'),
        (CAVING, 'Spéléologie'),
        (MOUNTAINEERING, 'Alpinisme'),
    )

    STATE_CHOICES = (
        (PLACED_STATE, 'Commande effectuée'),
        (PREPARED_STATE, 'Commande préparée'),
        (SOLD_STATE, 'Commande distribuée'),
    )

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
