from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from . import validators


def get_previous_stock(id_):
    try:
        return VoucherOperation.objects.get(id=id_-1).stock
    except ObjectDoesNotExist:
        return 0


def get_stock():
    try:
        return VoucherOperation.objects.latest('id').stock
    except ObjectDoesNotExist:
        return 0


def update_stock(delta, reason):
    stock = get_stock() + delta

    if stock < 0:
        raise ValueError("Il ne reste pas suffisamment de bons.")

    op = VoucherOperation(stock=stock, reason=reason)
    op.save()
    return op


def voucher_distrib_to_amount(distribution):
    amount = 0
    for k, v in distribution.items():
        amount += k * v
    return amount


def add_voucher_distribs(d1, d2):
    for k, v in d2.items():
        d1[k] += v


class VoucherOperation(models.Model):
    REASON_MAX_LEN = 200

    stock = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
    )
    reason = models.CharField(max_length=REASON_MAX_LEN,)

    def __str__(self):
        return str(self.id)

    @property
    def delta(self):
        return self.stock - get_previous_stock(self.id)
