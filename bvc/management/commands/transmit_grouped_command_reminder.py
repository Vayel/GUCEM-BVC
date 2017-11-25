from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist

from bvc.models import GroupedCommand, command

from ._reminder import ReminderCommand


class Command(ReminderCommand):
    help = 'Remind the treasurer to transmit the grouped command to the shop.'

    def handle(self, *args, **options):
        try:
            cmd = GroupedCommand.objects.get(state=command.PLACED_STATE)
        except ObjectDoesNotExist:
            return

        # An email has already been sent when the grouped command was placed
        # so we don't need to send a reminder the same day
        if datetime.now().day != cmd.datetime_placed.day:
            cmd.send_place_email(reminder=True)
