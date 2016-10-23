from django.db import models
from django.core.exceptions import ObjectDoesNotExist


def get_current_bank_deposit():
    try:
        return BankDeposit.objects.filter(datetime__isnull=True).latest('id')
    except ObjectDoesNotExist:
        return BankDeposit.objects.create()

def get_previous_treasury(id):
    try:
        return TreasuryOperation.objects.get(id=id-1).stock
    except ObjectDoesNotExist:
        return 0

def get_treasury():
    try:
        return TreasuryOperation.objects.latest('id').stock
    except ObjectDoesNotExist:
        return 0


class BankDeposit(models.Model):
    # If null, the deposit has not been done yet
    datetime = models.DateTimeField(null=True, blank=True,)

    def __str__(self):
        if self.datetime is None:
            return 'En cours'
        else:
            return self.datetime.strftime('%Y-%m-%d %H:%M')


class TreasuryOperation(models.Model):
    stock = models.PositiveSmallIntegerField()
    # If null, the operation does not come from a bank deposit
    bank_deposit = models.ForeignKey(BankDeposit, null=True, blank=True,)

    @property
    def amount(self):
        return self.stock - get_previous_treasury(self.id)
