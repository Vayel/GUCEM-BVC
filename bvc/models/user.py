from django.db import models
from django.conf import settings


class Member(models.Model):
    ESMUG = 'esmug' # -15%
    GUCEM = 'gucem' # -18%

    CLUB_CHOICES = (
        (GUCEM, 'GUCEM'),
        (ESMUG, 'ESMUG'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    license = models.CharField(max_length=12, unique=True,)
    club = models.CharField(
        max_length=max(len(choice[0]) for choice in CLUB_CHOICES),
        choices=CLUB_CHOICES,
        default=GUCEM,
    )
    vip = models.BooleanField(default=False) # -20%

    def __str__(self):
        return '{} {}'.format(
            self.user.first_name,
            self.user.last_name,
        )

    @property
    def type(self):
        if self.vip:
            return 'VIP'
        else:
            return self.club

class Commission(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.user.username
