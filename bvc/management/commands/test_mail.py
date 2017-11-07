import io
import csv
from smtplib import SMTPException

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings

from bvc import utils


class Command(BaseCommand):
    def handle(self, *args, **options):
        csvfile = io.StringIO()
        writer = csv.writer(csvfile)
        writer.writerow(['Col A', 'Col B',])

        email = EmailMessage(
            utils.format_mail_subject("Démarrage de l'application - mail test"),
            "Test de l'envoi des mails depuis l'application BVC.",
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            [],
        )
        email.attach('test.csv', csvfile.getvalue(), 'text/csv')
        if not email.send():
            raise SMTPException()
