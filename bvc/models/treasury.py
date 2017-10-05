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

    stock = models.DecimalField(max_digits=7, decimal_places=2, verbose_name='stock',)
    reason = models.CharField(max_length=REASON_MAX_LEN, verbose_name='raison',)
    date = models.DateField(auto_now_add=True,)

    class Meta:
        verbose_name = 'opération de trésorerie'
        verbose_name_plural = 'opérations de trésorerie'

    def __str__(self):
        return '{} (delta : {})'.format(self.stock, self.delta)

    @property
    def delta(self):
        return self.stock - get_previous_treasury(self.id)
