from django.db import models


def get_current_bank_deposit():
    try:
        return BankDeposit.objects.filter(datetime__isnull=True).latest('id')
    except ObjectDoesNotExist:
        return BankDeposit.objects.create()


class BankDeposit(models.Model):
    # If null, the deposit has not been done yet
    datetime = models.DateTimeField(null=True, blank=True,)

    def __str__(self):
        if self.datetime is None:
            return 'En cours'
        else:
            return self.datetime.strftime('%Y-%m-%d %H:%M')
