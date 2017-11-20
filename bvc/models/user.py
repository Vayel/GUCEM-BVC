from django.db import models
from django.conf import settings
from django.template.loader import render_to_string

from .configuration import get_config
from .. import utils


class AbstractUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='utilisateur',)
    receive_reminder = models.BooleanField(
        default=False,
        verbose_name='reçoit le mail de rappel',
    )

    class Meta:
        abstract = True

    def send_command_summary(self):
        self.user.email_user(
            utils.format_mail_subject('Vos commandes en cours'),
            render_to_string(
                'bvc/mails/command_summary.txt',
                {'commands': self.commands.all()}
            ),
            get_config().bvc_manager_mail
        )

    def remind_next_grouped_command(self):
        self.user.email_user(
            utils.format_mail_subject('La date limite de commande approche'),
            render_to_string(
                'bvc/mails/remind_next_grouped_command.txt',
                {'day': get_config().grouped_command_day - 1}
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

    license = models.CharField(max_length=12, unique=True, verbose_name='licence CAF',)
    club = models.CharField(
        max_length=max(len(choice[0]) for choice in CLUB_CHOICES),
        choices=CLUB_CHOICES,
        default=GUCEM,
        verbose_name='club',
    )

    class Meta:
        verbose_name = 'adhérent'

    def __str__(self):
        return '{} {} - {}'.format(
            self.user.first_name,
            self.user.last_name,
            self.user.email,
        )


class Commission(AbstractUser):
    class Meta:
        verbose_name = 'commission'

    def __str__(self):
        return self.user.username
