from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


def get_config():
    return Configuration.objects.last()


class Configuration(models.Model):
    esmug_percentage_discount = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)],
    )
    gucem_percentage_discount = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)],
    )

    bvc_manager_mail = models.EmailField()
    treasurer_mail = models.EmailField()

    grouped_command_extra_amount = models.PositiveSmallIntegerField()
    grouped_command_day = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(28)],  # February has only 28 days
    )
