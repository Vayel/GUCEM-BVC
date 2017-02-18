from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

MAX_DAY_NUMBER = 28  # February has only 28 days


def get_config():
    return Configuration.objects.last()


class Configuration(models.Model):
    esmug_percentage_discount = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)],
        verbose_name='réduction ESMUG (%)',
    )
    gucem_percentage_discount = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)],
        verbose_name='réduction GUCEM (%)',
    )

    bvc_manager_mail = models.EmailField(verbose_name='mail du responsable',)
    treasurer_mail = models.EmailField(verbose_name='mail du trésorier',)

    grouped_command_extra_amount = models.PositiveSmallIntegerField(
        verbose_name='marge des commandes groupées',
    )
    grouped_command_day = models.PositiveSmallIntegerField(
        # The minimum is 2 because the day before is the last one to place commands
        # and it must be fixed. If grouped_command_day == 1, the last day to
        # order vouchers can be 30, 31, 28, 29, and it is not convenient.
        validators=[MinValueValidator(2), MaxValueValidator(MAX_DAY_NUMBER)],
        verbose_name='jour de commande groupée',
    )
