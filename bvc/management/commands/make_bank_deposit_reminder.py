from ._reminder import ReminderCommand


class Command(ReminderCommand):
    help = 'Remind the manager to make a bank deposit.'

    def handle(self, *args, **options):
        super().handle(
            'bvc/mails/make_bank_deposit_reminder.txt',
            {},
            'Rappel : dépôt en banque',
            *args, **options
        )
