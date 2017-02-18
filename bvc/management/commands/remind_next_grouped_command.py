from itertools import chain

from django.core.management.base import BaseCommand

from bvc.models import Commission, Member


class Command(BaseCommand):
    help = 'Warn users about the last day to command approaching.'

    def handle(self, *args, **options):
        members = Member.objects.filter(receive_reminder=True)
        commissions = Commission.objects.filter(receive_reminder=True)

        for user in chain(members, commissions):
            user.remind_next_grouped_command()
