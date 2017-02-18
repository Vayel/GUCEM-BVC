from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string

from bvc.models import get_config
from bvc import utils


class ReminderCommand(BaseCommand):
    def handle(self, template, context, subject, *args, to=None, **options):
        send_mail(
            utils.format_mail_subject(subject),
            render_to_string(template, context),
            get_config().bvc_manager_mail,
            to or [get_config().bvc_manager_mail],
        )
