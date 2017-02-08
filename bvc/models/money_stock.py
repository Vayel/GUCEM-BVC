import io
import csv

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from .command import *
from .. import utils


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

def fill_deposit_file_header(writer, deposit):
    writer.writerow([str(deposit)])
    writer.writerow([])
    writer.writerow(['Numéro de remise', deposit.bank_deposit.ref])
    writer.writerow(['Date', deposit.bank_deposit.datetime])
    writer.writerow([])

def fill_deposit_file_commands(writer, deposit):
    writer.writerow(['Nom', 'Prénom', 'Type', 'License', 'Bons', 'Prix'])

    for cmd in deposit.bank_deposit.commands.all():
        writer.writerow([cmd.member.user.last_name, cmd.member.user.first_name,
                         cmd.member.type, cmd.member.license, cmd.amount, cmd.price])

    writer.writerow([])

def send_deposit_file(func):
    def wrapper(deposit, *args, **kwargs):
        csvfile = io.StringIO()
        writer = csv.writer(csvfile)
        fill_deposit_file_header(writer, deposit)
        fill_deposit_file_commands(writer, deposit)

        func(writer, deposit, *args, **kwargs)

        email = EmailMessage(
            utils.format_mail_subject(str(deposit)),
            render_to_string(
                'bvc/mails/bank_deposit_summary.txt',
                {'name': str(deposit),},
            ),
            settings.BVC_MANAGER_MAIL,
            [settings.TREASURER_MAIL],
            [],
        )
        email.attach(slugify(str(deposit)) + '.csv', csvfile.getvalue(), 'text/csv')
        email.send()

    return wrapper

@send_deposit_file
def send_check_deposit_file(writer, deposit):
    writer.writerow(['', '', '', '', 'Total déposé', deposit.total_price])

@send_deposit_file
def send_cash_deposit_file(writer, deposit):
    writer.writerow(['', '', '', '', 'Total commandes', deposit.total_command_price])
    writer.writerow(['', '', '', '', 'Delta trésorerie', deposit.treasury_operation.delta ])
    writer.writerow(['', '', '', '', 'Total déposé', deposit.total_price])

def send_deposit_file_callback(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        if sender == CashBankDeposit:
            send_cash_deposit_file(instance)
        elif sender == CheckBankDeposit:
            send_check_deposit_file(instance)

post_save.connect(send_deposit_file_callback)


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
        return 'BVC {}'.format(self.id)

    @property
    def total_price(self):
        return sum(cmd.price for cmd in self.bank_deposit.commands.all())


class CashBankDeposit(models.Model):
    bank_deposit = models.OneToOneField(BankDeposit, related_name='cash_deposit')
    treasury_operation = models.OneToOneField(TreasuryOperation, related_name='bank_deposit',)

    def __str__(self):
        return 'BVE {}'.format(self.id)

    @property
    def total_command_price(self):
        return sum(cmd.price for cmd in self.bank_deposit.commands.all())

    @property
    def total_price(self):
        return self.total_command_price - self.treasury_operation.delta 
