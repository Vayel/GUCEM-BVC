from ._reminder import ReminderCommand


class Command(ReminderCommand):
    help = 'Remind the manager to send the mail warning users about command cancellation.'

    def handle(self, *args, **options):
        super().handle(
            'bvc/mails/warn_about_cancellation_reminder.txt',
            {},
            'Rappel : commandes bientôt annulées',
            *args, **options
        )
