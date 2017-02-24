from functools import partial

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

MAX_DAY_NUMBER = 28  # February has only 28 days


def get_config():
    return Configuration.objects.last()


def get_config_val(key):
    cfg = get_config()

    if cfg is None:
        return None

    return cfg.__dict__.get(key, None)


# One row is created each time the configuration is modified to keep an history
# of old values. So we need to set default values to current ones.
class Configuration(models.Model):
    esmug_percentage_discount = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)],
        verbose_name='réduction ESMUG (%)',
        default=partial(get_config_val, 'esmug_percentage_discount'),
    )
    gucem_percentage_discount = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)],
        verbose_name='réduction GUCEM (%)',
        default=partial(get_config_val, 'gucem_percentage_discount'),
    )

    bvc_manager_mail = models.EmailField(
        verbose_name='mail du responsable',
        default=partial(get_config_val, 'bvc_manager_mail'),
    )
    treasurer_mail = models.EmailField(
        verbose_name='mail du trésorier',
        default=partial(get_config_val, 'treasurer_mail'),
    )

    grouped_command_extra_amount = models.PositiveSmallIntegerField(
        verbose_name='marge des commandes groupées',
        default=partial(get_config_val, 'grouped_command_extra_amount'),
    )
    grouped_command_day = models.PositiveSmallIntegerField(
        # The minimum is 2 because the day before is the last one to place commands
        # and it must be fixed. If grouped_command_day == 1, the last day to
        # order vouchers can be 30, 31, 28, 29, and it is not convenient.
        validators=[MinValueValidator(2), MaxValueValidator(MAX_DAY_NUMBER)],
        verbose_name='jour de commande groupée',
        default=partial(get_config_val, 'grouped_command_day'),
    )
