from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


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
        validators=[MinValueValidator(1), MaxValueValidator(28)],  # February has only 28 days
        verbose_name='jour de commande groupée',
    )
