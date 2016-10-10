from django.db import models

from . import validators

class Operation(models.Model):
    MEMBER_COMMAND = 'member'
    COMMISSION_COMMAND = 'commission'
    GROUPED_COMMAND = 'grouped'

    COMMAND_TYPE_CHOICES = (
        (MEMBER_COMMAND, 'Membre'),
        (COMMISSION_COMMAND, 'Commission'),
        (GROUPED_COMMAND, 'Groupée'),
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
