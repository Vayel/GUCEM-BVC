from ._reminder import ReminderCommand


class Command(ReminderCommand):
    help = 'Remind the manager to place a grouped command.'

    def handle(self, *args, **options):
        super().handle(
            'bvc/mails/place_grouped_command_reminder.txt',
            {},
            'Rappel : commande groupée',
        )
