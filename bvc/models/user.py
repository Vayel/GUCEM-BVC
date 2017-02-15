from django.db import models
from django.conf import settings
from django.template.loader import render_to_string

from .configuration import get_config
from .. import utils


class AbstractUser(models.Model):
    class Meta:
        abstract = True

    def send_command_summary(self):
        self.user.email_user(
            utils.format_mail_subject('Récapitulatif des commandes'),
            render_to_string(
                'bvc/mails/command_summary.txt',
                {'commands': self.commands.all()}
            ),
            get_config().bvc_manager_mail
        )


class Member(AbstractUser):
    ESMUG = 'esmug'
    GUCEM = 'gucem'

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

    def __str__(self):
        return '{} {}'.format(
            self.user.first_name,
            self.user.last_name,
        )


class Commission(AbstractUser):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.user.username
