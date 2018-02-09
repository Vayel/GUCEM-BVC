import io
import csv

from django.db import models
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.text import slugify

from .command import *
from .configuration import get_config
from .treasury import TreasuryOperation

from .. import utils


class InvalidState(Exception): pass

def fill_deposit_file_header(writer, deposit):
    writer.writerow([str(deposit)])
    writer.writerow([])
    writer.writerow(['Numéro de remise', deposit.bank_deposit.ref])
    writer.writerow(['Date', deposit.bank_deposit.datetime])
    writer.writerow([])


def fill_deposit_file_commands(writer, deposit):
    writer.writerow(['Id', 'Nom', 'Prénom', 'Type', 'License', 'Bons', 'Prix'])

    for cmd in deposit.bank_deposit.commands.all():
        writer.writerow([cmd.id, cmd.member.user.last_name, cmd.member.user.first_name,
                         cmd.member.club, cmd.member.license, cmd.amount, cmd.price])

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
            get_config().bvc_manager_mail,
            [get_config().treasurer_mail],
            [],
        )
        email.attach(slugify(str(deposit)) + '.csv', csvfile.getvalue(), 'text/csv')
        email.send()

    return wrapper


@send_deposit_file
def send_check_deposit_file(writer, deposit):
    writer.writerow(['', '', '', '', '', 'Total déposé', deposit.total_price])


@send_deposit_file
def send_cash_deposit_file(writer, deposit):
    writer.writerow(['', '', '', '', '', 'Total commandes', deposit.total_command_price])
    writer.writerow(['', '', '', '', '', 'Delta trésorerie', deposit.treasury_operation.delta])
    writer.writerow(['', '', '', '', '', 'Total déposé', deposit.total_price])


class BankDeposit(models.Model):
    REF_MAX_LEN = 20

    datetime = models.DateField(verbose_name='date')
    ref = models.CharField(max_length=REF_MAX_LEN, verbose_name='référence')
    made = models.BooleanField(default=False, verbose_name='déposé',)

    def __str__(self):
        return '{0} (ref {1})'.format(self.datetime.strftime('%Y-%m-%d'), self.ref)


class CheckBankDeposit(models.Model):
    # Use OneToOneField to be able to refer to bank deposit by a foreign key
    bank_deposit = models.OneToOneField(
        BankDeposit,
        related_name='check_deposit',
        verbose_name='dépôt',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Dépôt de chèques'
        verbose_name_plural = "Dépôts de chèques"

    def __str__(self):
        return 'BVC {} (id {})'.format(self.bank_deposit, self.id)

    @property
    def total_price(self):
        return sum(cmd.price for cmd in self.bank_deposit.commands.all())

    def make(self):
        if self.bank_deposit.made:
            raise InvalidState()

        send_check_deposit_file(self)

        self.bank_deposit.made = True
        self.bank_deposit.save()

    @classmethod
    def next_id(cls):
        last = cls.objects.last()
        if last is None:
            return 1
        else:
            return last.id + 1


class CashBankDeposit(models.Model):
    bank_deposit = models.OneToOneField(
        BankDeposit,
        related_name='cash_deposit',
        verbose_name='dépôt',
        on_delete=models.CASCADE,
    )
    treasury_operation = models.OneToOneField(
        TreasuryOperation,
        related_name='bank_deposit',
        verbose_name='opération sur la trésorerie',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Dépôt d'espèces"
        verbose_name_plural = "Dépôts d'espèces"

    def __str__(self):
        return 'BVE {} (id {})'.format(self.bank_deposit, self.id)

    @property
    def total_command_price(self):
        return int(sum(cmd.price for cmd in self.bank_deposit.commands.all()))

    @property
    def total_price(self):
        return self.total_command_price - self.treasury_operation.delta

    def make(self):
        if self.bank_deposit.made:
            raise InvalidState()

        send_cash_deposit_file(self)

        self.bank_deposit.made = True
        self.bank_deposit.save()

    @classmethod
    def next_id(cls):
        last = cls.objects.last()
        if last is None:
            return 1
        else:
            return last.id + 1
