from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from . import validators

def get_stock():
    try:
        return VoucherOperation.objects.latest('id').stock
    except ObjectDoesNotExist:
        return 0

def update_stock(type, id, delta):
    stock = get_stock() + delta

    if stock < 0:
        raise ValueError("Il ne reste pas suffisamment de bons.")

    VoucherOperation(
        command_type=type,
        command_id=id, 
        stock=stock,
    ).save()

class VoucherOperation(models.Model):
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
        validators=[validators.validate_voucher_amount_multiple],
    )

    def __str__(self):
        return '{} - Stock = {}'.format(self.id, self.stock)
