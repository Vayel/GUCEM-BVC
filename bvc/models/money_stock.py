from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from .command import *


def get_current_bank_deposit(type_):
    if type_ == CASH_PAYMENT:
        model = CashBankDeposit
    elif type_ == CHECK_PAYMENT:
        model = CheckBankDeposit
    else:
        raise ValueError()

    try:
        return model.objects.filter(datetime__isnull=True).latest('id')
    except ObjectDoesNotExist:
        return model.objects.create()

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

    stock = models.PositiveSmallIntegerField()
    reason = models.CharField(max_length=REASON_MAX_LEN,)

    @property
    def delta(self):
        return self.stock - get_previous_treasury(self.id)


class BankDeposit(models.Model):
    REF_MAX_LEN = 20

    # If null, the deposit has not been done yet
    datetime = models.DateField()
    ref = models.CharField(max_length=REF_MAX_LEN,)

    def __str__(self):
        if self.datetime is None:
            return 'En cours'
        else:
            return self.datetime.strftime('%Y-%m-%d %H:%M')


class CheckBankDeposit(models.Model):
    # Use OneToOneField to be able to refer to bank deposit by a foreign key
    bank_deposit = models.OneToOneField(BankDeposit, related_name='check_deposit')

    def __str__(self):
        return str(self.bank_deposit)


class CashBankDeposit(models.Model):
    bank_deposit = models.OneToOneField(BankDeposit, related_name='cash_deposit')
    treasury_operation = models.OneToOneField(TreasuryOperation, related_name='bank_deposit',)

    def __str__(self):
        return str(self.bank_deposit)
