from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

from .. import models
from .. import utils


def get_last_grouped_command():
    try:
        return models.command.GroupedCommand.objects.latest('id')
    except ObjectDoesNotExist:
        return None

class PlaceGroupedCommand(TestCase):
    def setUp(self):
        DEFAULT_MEMBER_USER = User.objects.create_user(
            'member',
            'x@y.z'
            '',
        )
        self.DEFAULT_MEMBER = models.user.Member.objects.create(
            user=DEFAULT_MEMBER_USER,
            license='AAAAXXYY',
            club=models.user.Member.GUCEM,
        )

        DEFAULT_COMMISSION_USER = User.objects.create_user(
            'commission',
            'a@b.c'
            '',
        )
        self.DEFAULT_COMMISSION = models.user.Commission.objects.create(
            user=DEFAULT_COMMISSION_USER,
            type='caving',
        )

        self.placed_amounts = [200, 1000]
        self.setup_datetime = now()

        models.command.MemberCommand.objects.create(
            member=self.DEFAULT_MEMBER,
            amount=self.placed_amounts[0],
        )
        models.command.CommissionCommand.objects.create(
            commission=self.DEFAULT_COMMISSION,
            amount=self.placed_amounts[1],
        )

    def test_get(self):
        resp = self.client.get(reverse('bvc:place_grouped_command'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(get_last_grouped_command(), None)

    def test_without_cancel(self):
        resp = self.client.post(reverse('bvc:place_grouped_command'))
        self.assertEqual(resp.status_code, 302)

        cmd = get_last_grouped_command()
        self.assertEqual(
            cmd.placed_amount,
            (sum(self.placed_amounts) + settings.VOUCHER_STOCK_MIN +
            settings.GROUPED_COMMAND_EXTRA_AMOUNT),
        )
        self.assertEqual(cmd.received_amount, 0)
        self.assertEqual(cmd.prepared_amount, 0)
        self.assertTrue(self.setup_datetime < cmd.datetime_placed < now())
        self.assertEqual(cmd.datetime_received, None)
        self.assertEqual(cmd.datetime_prepared, None)
        self.assertEqual(cmd.state, models.command.PLACED_STATE)

    def test_with_cancel(self):
        cmd = models.command.MemberCommand.objects.create(
            member=self.DEFAULT_MEMBER,
            amount=300,
            state=models.command.PREPARED_STATE,
        )
        cmd.save()

        resp = self.client.post(reverse('bvc:place_grouped_command'))
        self.assertEqual(resp.status_code, 302)

        grouped_cmd = get_last_grouped_command()
        self.assertEqual(
            grouped_cmd.placed_amount,
            (sum(self.placed_amounts) + settings.VOUCHER_STOCK_MIN +
            settings.GROUPED_COMMAND_EXTRA_AMOUNT - cmd.amount),
        )

        operation = models.voucher.Operation.objects.first()
        self.assertEqual(operation.command_type, models.voucher.Operation.MEMBER_COMMAND)
        self.assertEqual(operation.command_id, cmd.id)
        self.assertEqual(operation.stock, cmd.amount)

    def test_with_placed_grouped_command(self):
        self.client.post(reverse('bvc:place_grouped_command'))
        self.client.post(reverse('bvc:place_grouped_command'))

        self.assertEqual(
            models.command.GroupedCommand.objects.count(),
            1
        )
    
    def test_with_received_grouped_command(self):
        self.client.post(reverse('bvc:place_grouped_command'))

        cmd = models.command.GroupedCommand.objects.last()
        cmd.state = models.command.PREPARED_STATE 
        cmd.save()

        self.client.post(reverse('bvc:place_grouped_command'))

        self.assertEqual(
            models.command.GroupedCommand.objects.count(),
            2
        )
