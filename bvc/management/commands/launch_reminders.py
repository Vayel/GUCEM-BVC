from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from bvc.models import get_config, BankDeposit, GroupedCommand

from . import make_bank_deposit_reminder
from . import place_grouped_command_reminder
from . import warn_about_cancellation_reminder


class Command(BaseCommand):
    def handle(self, *args, **options):
        cfg = get_config()
        now = datetime.now()
        grouped_cmd_date = now.replace(day=cfg.grouped_command_day)

        # Place grouped command
        try:
            last_grouped_cmd_date = GroupedCommand.objects.last().datetime_placed
        except ObjectDoesNotExist:
            remind = True
        else:
            # Do not remind if the command has already been placed
            remind = last_grouped_cmd_date.replace(tzinfo=None) < grouped_cmd_date
        finally:
            if now.day == grouped_cmd_date.day and remind:
                self.stdout.write('Place grouped command')
                place_grouped_command_reminder.Command().handle()

        # Make bank deposit
        bank_deposit_remind_date = grouped_cmd_date + timedelta(days=3)
        try:
            last_deposit_date = BankDeposit.objects.last().datetime
        except ObjectDoesNotExist:
            remind = True
        else:
            # Do not remind if the deposit has already been made
            remind = last_deposit_date < grouped_cmd_date.date()
        finally:
            if now.day == bank_deposit_remind_date.day and remind:
                self.stdout.write('Make bank deposit')
                make_bank_deposit_reminder.Command().handle()

        # Warn about cancellation
        if now.day == (grouped_cmd_date - timedelta(days=8)).day:
            self.stdout.write('Warn about cancellation')
            warn_about_cancellation_reminder.Command().handle()
