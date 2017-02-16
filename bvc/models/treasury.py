from django.db import models
from django.core.exceptions import ObjectDoesNotExist


def get_previous_treasury(id_):
    try:
        return TreasuryOperation.objects.get(id=id_-1).stock
    except ObjectDoesNotExist:
        return 0


def get_treasury():
    try:
        return TreasuryOperation.objects.latest('id').stock
    except ObjectDoesNotExist:
        return 0


def treasury_op_from_delta(delta, reason):
    stock = get_treasury() + delta
    if stock < 0:
        raise ValueError()

    op = TreasuryOperation(stock=stock, reason=reason)
    op.save()
    return op


class TreasuryOperation(models.Model):
    REASON_MAX_LEN = 200

    stock = models.PositiveSmallIntegerField(verbose_name='stock',)
    reason = models.CharField(max_length=REASON_MAX_LEN, verbose_name='raison',)

    class Meta:
        verbose_name = 'Opération de trésorerie'
        verbose_name_plural = 'Opérations de trésorerie'

    @property
    def delta(self):
        return self.stock - get_previous_treasury(self.id)
