from django.db import models
from django.utils.timezone import now
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .command import *
from .configuration import get_config
from . import validators
from . import voucher

from .. import utils


class IndividualCommand(models.Model):
    """Represent a command placed to the manager."""
    amount = models.PositiveSmallIntegerField( # Amount before reduction
        default=0,
        validators=[validators.validate_voucher_amount_multiple],
        verbose_name='montant',
        help_text='Avant réduction.',
    )
    comments = models.TextField(default='', blank=True, verbose_name='commentaires',)
    datetime_placed = models.DateTimeField(auto_now_add=True, verbose_name='date')
    datetime_prepared = models.DateField(null=True, blank=True, verbose_name='date de préparation',)
    datetime_cancelled = models.DateField(null=True, blank=True, verbose_name="date d'annulation",)
    # To make packets with high-value vouchers only.
    # For intance, if a member places a command to buy a 500-euro object, we can
    # give him 10 vouchers of 50 euros (he does not need 10-euro or 20-euro vouchers).
    spent_at_once = models.BooleanField(default=False, verbose_name='dépensée en une fois',)

    class Meta:
        abstract = True

    @classmethod
    def get_total_amount(cls, states):
        total = cls.objects.filter(state__in=states).aggregate(models.Sum('amount'))['amount__sum']
        return total or 0

    @property
    def voucher_distrib(self):
        return voucher.get_distrib(self.amount, self.spent_at_once)

    @property
    def n_vouchers_10(self):
        return self.voucher_distrib[10]

    @property
    def n_vouchers_20(self):
        return self.voucher_distrib[20]

    @property
    def n_vouchers_50(self):
        return self.voucher_distrib[50]

    @property
    def email(self):
        raise NotImplementedError()

    # Define this property in the abstract class to have a common interface for
    # the templates
    @property
    def price(self):
        return 0

    def amount_changed(self, old_amount):
        if old_amount == self.amount:
            return

        voucher.update_stock(old_amount - self.amount, str(self))
    
    def send_preparation_email(self):
        send_mail(
            utils.format_mail_subject('Commande en cours de préparation'),
            render_to_string(
                'bvc/mails/command_being_prepared.txt',
                {
                    'amount': self.amount,
                    'price': self.price,
                }
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )

    def prepare(self):
        if self.state != TO_BE_PREPARED_STATE:
            raise InvalidState(
                "La commande {} n'est pas dans le bon état pour être préparée.".format(self)
            )

        voucher.update_stock(-self.amount, str(self))        

        self.state = PREPARED_STATE
        self.datetime_prepared = now()
        self.save()

        send_mail(
            utils.format_mail_subject('Commande reçue'),
            render_to_string(
                'bvc/mails/command_prepared.txt',
                {
                    'amount': self.amount,
                    'price': self.price,
                }
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )

    def warn_about_cancellation(self):
        if self.state != PREPARED_STATE:
            raise InvalidState("La commande {} n'est pas préparée, impossible "
                               "de prévenir son annulation.".format(self))

        send_mail(
            utils.format_mail_subject('Commande bientôt annulée'),
            render_to_string(
                'bvc/mails/cancel_command_soon.txt',
                {'cmd': self, 'grouped_command_day': get_config().grouped_command_day}
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )

    def cancel(self):
        if self.state not in [PLACED_STATE, TO_BE_PREPARED_STATE, PREPARED_STATE]:
            raise InvalidState("La commande {} n'est pas dans le bon état pour être annulée.".format(self))

        if self.state == PREPARED_STATE:
            voucher.update_stock(self.amount, str(self))

        self.state = CANCELLED_STATE
        self.datetime_cancelled = now()
        self.save()

        send_mail(
            utils.format_mail_subject('Commande annulée'),
            render_to_string(
                'bvc/mails/cancel_command.txt',
                {
                    'amount': self.amount,
                    'date': self.datetime_placed,
                }
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )

    def uncancel(self):
        if self.state != CANCELLED_STATE:
            raise InvalidState("La commande {} n'est pas dans le bon état pour être désannulée.".format(self))

        self.state = PLACED_STATE
        datetime_cancelled = self.datetime_cancelled
        self.datetime_cancelled = None
        self.save()

        send_mail(
            utils.format_mail_subject('Commande désannulée'),
            render_to_string(
                'bvc/mails/uncancel_command.txt',
                {
                    'amount': self.amount,
                    'cancel_date': datetime_cancelled,
                }
            ),
            get_config().bvc_manager_mail,
            [self.email],
        )
