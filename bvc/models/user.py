from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
    ESMUG = 'esmug' # -15%
    GUCEM = 'gucem' # -18%

    CLUB_CHOICES = (
        (GUCEM, 'GUCEM'),
        (ESMUG, 'ESMUG'),
    )

    user = models.OneToOneField(User)
    license = models.CharField(max_length=12, unique=True,)
    club = models.CharField(
        max_length=max(len(choice[0]) for choice in CLUB_CHOICES),
        choices=CLUB_CHOICES,
        default=GUCEM,
    )
    vip = models.BooleanField(default=False) # -20%

    def __str__(self):
        return '{} {} (n°{})'.format(
            self.user.first_name,
            self.user.last_name,
            self.license,
        )

class Commission(models.Model):
    user = models.OneToOneField(User)
    type = models.CharField(max_length=30, unique=True,)

    def __str__(self):
        return self.type
