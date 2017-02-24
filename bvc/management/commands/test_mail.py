from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_mail(
            'BVC - Mail test',
            "Test de l'envoi des mails depuis l'application BVC.",
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
        )
