from django.test import TestCase, Client
from django.contrib.auth.models import User
from player.models import Wallet


class HomeTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='test1',
            password='Password1'
        )

        self.real_wallet = Wallet.objects.create(
            money_type='EUR',
            owner=self.user,
            balance=0
        )

    def test_deposit_money(self):
        self.client.force_login(self.user)
        self.client.post('/player/deposit/', {'amount': 10})
        self.assertEqual(Wallet.objects.get(pk=self.real_wallet.pk).balance, 10)


class DepositMoneyTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='test1',
            password='Password1'
        )

        self.real_wallet = Wallet.objects.create(
            money_type='EUR',
            owner=self.user,
            balance=0
        )

    def test_deposit_money(self):
        self.client.force_login(self.user)
        self.client.post('/player/deposit/', {'amount': 10})
        self.assertEqual(Wallet.objects.get(pk=self.real_wallet.pk).balance, 10)
