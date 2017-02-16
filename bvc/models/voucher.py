from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from . import validators

VOUCHER_SUBPACKET_AMOUNT = 500


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


def distrib_to_amount(distribution):
    amount = 0
    for k, v in distribution.items():
        amount += k * v
    return amount


def get_distrib(amount, sold_at_once=False):
    if sold_at_once:
        # Give one 10 then 50, then 20, then 10
        default_10 = 1
        remaining = amount - default_10 * 10

        return {
            10: default_10 + ((remaining % 50) % 20) // 10,
            20: (remaining % 50) // 20,
            50: remaining // 50,
        }

    if amount <= 0:
        return {10: 0, 20: 0, 50: 0,}
    if amount <= 100:
        # Only 10
        return {10: amount // 10, 20: 0, 50: 0,}
    if amount <= 200:
        # 10 * 10, the rest with 20 then 10
        default_10 = 10
        remaining = amount - 10 * default_10

        return {
            10: default_10 + (remaining % 20) // 10,
            20: remaining // 20,
            50: 0,
        }
    if amount < VOUCHER_SUBPACKET_AMOUNT:
        # 10 * 10, 5 * 20, the rest with 50, 20 then 10
        default_10 = 10
        default_20 = 5
        remaining = amount - 10 * default_10 - 20 * default_20

        return {
            10: default_10 + ((remaining % 50) % 20) // 10,
            20: default_20 + (remaining % 50) // 20,
            50: remaining // 50,
        }

    subpacket_distrib = get_distrib(amount - VOUCHER_SUBPACKET_AMOUNT)
    subpacket_distrib[10] += 10
    subpacket_distrib[20] += 5
    subpacket_distrib[50] += 6

    return subpacket_distrib


def get_commands_distrib(commands):
    distribution = get_distrib(0)

    for cmd in commands:
        add_distribs(distribution, cmd.voucher_distrib)

    return distribution


def add_distribs(d1, d2):
    for k, v in d2.items():
        d1[k] += v


class VoucherOperation(models.Model):
    REASON_MAX_LEN = 200

    stock = models.PositiveSmallIntegerField(
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
        verbose_name='stock',
    )
    reason = models.CharField(max_length=REASON_MAX_LEN, verbose_name='raison',)

    class Meta:
        verbose_name = 'opération de bons'
        verbose_name_plural = 'opérations de bons'

    def __str__(self):
        return str(self.id)

    @property
    def delta(self):
        return self.stock - get_previous_stock(self.id)
