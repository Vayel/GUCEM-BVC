from django.db import models

from . import validators

class Operation(models.Model):
    PLUS_TYPE = 'plus'
    MINUS_TYPE = 'minus'

    MEMBER_COMMAND = 'member'
    COMMISSION_COMMAND = 'commission'
    GROUPED_COMMAND = 'grouped'

    TYPE_CHOICES = (
        (PLUS_TYPE, 'Ajout'),
        (MINUS_TYPE, 'Retrait'),
    )

    COMMAND_TYPE_CHOICES = (
        (MEMBER_COMMAND, 'Membre'),
        (COMMISSION_COMMAND, 'Commission'),
        (GROUPED_COMMAND, 'Groupée'),
    )

    type = models.CharField(
        max_length=max(len(choice[0]) for choice in TYPE_CHOICES),
        choices=TYPE_CHOICES,
        default=PLUS_TYPE,
    )
    command_type = models.CharField(
        max_length=max(len(choice[0]) for choice in COMMAND_TYPE_CHOICES),
        choices=COMMAND_TYPE_CHOICES,
        default=MEMBER_COMMAND,
    )
    command_id = models.PositiveIntegerField()
    stock = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_amount_multiple],
    )
