import os

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.conf import settings

from bvc import models


class IndividualCommandTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            'user',
            os.environ['BVC_MANAGER_MAIL'],
            '',
        )
        member = models.user.Member.objects.create(
            user=user,
            license='AAAAXXYY',
            club=models.user.Member.GUCEM,
        )
        commission = models.user.Commission.objects.create(
            user=user,
            type='caving',
        )

        self.placed = models.MemberCommand.objects.create(
            member=member,
            amount=100,
        )
        self.prepared = models.MemberCommand.objects.create(
            member=member,
            amount=100,
            state=models.command.PREPARED_STATE,
            datetime_prepared=now(),
        )
        self.sold = models.MemberCommand.objects.create(
            member=member,
            amount=100,
            state=models.command.SOLD_STATE,
            datetime_prepared=now(),
            datetime_sold=now(),
            payment_type=models.MemberCommand.CHECK_PAYMENT,
        )
        self.cashed = models.MemberCommand.objects.create(
            member=member,
            amount=100,
            state=models.command.CASHED_STATE,
            datetime_prepared=now(),
            datetime_sold=now(),
            datetime_cashed=now(),
            payment_type=models.MemberCommand.CHECK_PAYMENT,
        )
        self.cancelled = models.MemberCommand.objects.create(
            member=member,
            amount=100,
            state=models.command.CANCELLED_STATE,
            datetime_cancelled=now(),
        )
        self.given = models.CommissionCommand.objects.create(
            commission=commission,
            amount=100,
            state=models.command.GIVEN_STATE,
            datetime_prepared=now(),
            datetime_given=now(),
        )

        models.voucher.update_stock(
            models.voucher.Operation.MEMBER_COMMAND,
            1,
            1000
        )

    def test_prepare(self):
        with self.assertRaises(models.command.InvalidState) as context:
            self.prepared.prepare()
        with self.assertRaises(models.command.InvalidState) as context:
            self.sold.prepare()
        with self.assertRaises(models.command.InvalidState) as context:
            self.cashed.prepare()
        with self.assertRaises(models.command.InvalidState) as context:
            self.cancelled.prepare()
        with self.assertRaises(models.command.InvalidState) as context:
            self.given.prepare()

        old_stock = models.voucher.get_stock()

        self.placed.prepare()
        self.assertEquals(self.placed.state, models.command.PREPARED_STATE)
        self.assertTrue(self.placed.datetime_prepared is not None)
        self.assertEquals(old_stock - self.placed.amount, models.voucher.get_stock())

    def test_cancel(self):
        with self.assertRaises(models.command.InvalidState) as context:
            self.sold.cancel()
        with self.assertRaises(models.command.InvalidState) as context:
            self.cashed.cancel()
        with self.assertRaises(models.command.InvalidState) as context:
            self.given.cancel()
        with self.assertRaises(models.command.InvalidState) as context:
            self.cancelled.cancel()

        old_stock = models.voucher.get_stock()

        self.placed.cancel()
        self.assertEquals(self.placed.state, models.command.CANCELLED_STATE)
        self.assertTrue(self.placed.datetime_cancelled is not None)
        self.assertEquals(old_stock, models.voucher.get_stock())

        self.prepared.cancel()
        self.assertEquals(self.prepared.state, models.command.CANCELLED_STATE)
        self.assertTrue(self.prepared.datetime_cancelled is not None)
        self.assertEquals(old_stock + self.prepared.amount,
                          models.voucher.get_stock())

    def test_cancel_old(self):
        old_stock = models.voucher.get_stock()
        models.individual_command.cancel_old_commands()

        placed = models.MemberCommand.objects.get(id=self.placed.id)
        self.assertEquals(placed.state, models.command.PLACED_STATE)

        prepared = models.MemberCommand.objects.get(id=self.prepared.id)
        self.assertEquals(prepared.state, models.command.CANCELLED_STATE)
        self.assertTrue(prepared.datetime_cancelled is not None)
        self.assertEquals(old_stock + self.prepared.amount,
                          models.voucher.get_stock())


class CommissionCommandTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            'user',
            os.environ['BVC_MANAGER_MAIL'],
            '',
        )
        commission = models.user.Commission.objects.create(
            user=user,
            type='caving',
        )

        self.placed = models.CommissionCommand.objects.create(
            commission=commission,
            amount=100,
        )
        self.prepared = models.CommissionCommand.objects.create(
            commission=commission,
            amount=100,
            state=models.command.PREPARED_STATE,
            datetime_prepared=now(),
        )
        self.cancelled = models.CommissionCommand.objects.create(
            commission=commission,
            amount=100,
            state=models.command.CANCELLED_STATE,
            datetime_cancelled=now(),
        )
        self.given = models.CommissionCommand.objects.create(
            commission=commission,
            amount=100,
            state=models.command.GIVEN_STATE,
            datetime_prepared=now(),
            datetime_given=now(),
        )

    def test_email(self):
        self.assertEquals(self.placed.email, self.placed.commission.user.email)

    def test_discount(self):
        self.assertEquals(self.placed.discount, settings.VIP_DISCOUNT)

    def test_distribute(self):
        with self.assertRaises(models.command.InvalidState) as context:
            self.placed.distribute()
        with self.assertRaises(models.command.InvalidState) as context:
            self.given.distribute()
        with self.assertRaises(models.command.InvalidState) as context:
            self.cancelled.distribute()

        self.prepared.distribute()
        self.assertEquals(self.prepared.state, models.command.GIVEN_STATE)
        self.assertTrue(self.prepared.datetime_given is not None)


class MemberCommandTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            'user',
            os.environ['BVC_MANAGER_MAIL'],
            '',
        )
        user2 = User.objects.create_user(
            'user2',
            os.environ['TREASURER_MAIL'],
            '',
        )
        gucem = models.user.Member.objects.create(
            user=user,
            license='AAAAXXYY',
            club=models.user.Member.GUCEM,
        )
        esmug = models.user.Member.objects.create(
            user=user2,
            license='AAAAXXZZ',
            club=models.user.Member.ESMUG,
        )

        self.placed = models.MemberCommand.objects.create(
            member=gucem,
            amount=100,
        )
        self.prepared = models.MemberCommand.objects.create(
            member=esmug,
            amount=100,
            state=models.command.PREPARED_STATE,
            datetime_prepared=now(),
        )
        self.sold = models.MemberCommand.objects.create(
            member=gucem,
            amount=100,
            state=models.command.SOLD_STATE,
            datetime_prepared=now(),
            datetime_sold=now(),
            payment_type=models.MemberCommand.CHECK_PAYMENT,
        )
        self.cashed = models.MemberCommand.objects.create(
            member=esmug,
            amount=100,
            state=models.command.CASHED_STATE,
            datetime_prepared=now(),
            datetime_sold=now(),
            datetime_cashed=now(),
            payment_type=models.MemberCommand.CHECK_PAYMENT,
        )
        self.cancelled = models.MemberCommand.objects.create(
            member=gucem,
            amount=100,
            state=models.command.CANCELLED_STATE,
            datetime_cancelled=now(),
        )

    def test_email(self):
        self.assertEquals(self.placed.email, self.placed.member.user.email)

    def test_discount(self):
        self.assertEquals(self.placed.discount, settings.GUCEM_DISCOUNT)
        self.assertEquals(self.prepared.discount, settings.ESMUG_DISCOUNT)
        # TODO: VIP

    def test_sell(self):
        with self.assertRaises(models.command.InvalidState) as context:
            self.placed.sell(models.MemberCommand.CHECK_PAYMENT)
        with self.assertRaises(models.command.InvalidState) as context:
            self.sold.sell(models.MemberCommand.CHECK_PAYMENT)
        with self.assertRaises(models.command.InvalidState) as context:
            self.cashed.sell(models.MemberCommand.CHECK_PAYMENT)
        with self.assertRaises(models.command.InvalidState) as context:
            self.cancelled.sell(models.MemberCommand.CHECK_PAYMENT)

        self.prepared.sell(models.MemberCommand.CHECK_PAYMENT)
        self.assertEquals(self.prepared.state, models.command.SOLD_STATE)
        self.assertEquals(self.prepared.payment_type, models.MemberCommand.CHECK_PAYMENT)
        self.assertTrue(self.prepared.datetime_sold is not None)

    def test_cash(self):
        with self.assertRaises(models.command.InvalidState) as context:
            self.placed.cash()
        with self.assertRaises(models.command.InvalidState) as context:
            self.prepared.cash()
        with self.assertRaises(models.command.InvalidState) as context:
            self.cashed.cash()
        with self.assertRaises(models.command.InvalidState) as context:
            self.cancelled.cash()

        self.sold.cash()
        self.assertEquals(self.sold.state, models.command.CASHED_STATE)
        self.assertTrue(self.sold.datetime_cashed is not None)
