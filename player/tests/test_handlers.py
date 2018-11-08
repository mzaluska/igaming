from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from player.models import Bonus, WageringRequirement, Wallet
from player.signals import deposit_done


class BonusOnDepositHandlerTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test1',
            password='Password1'
        )

        self.deposit_bonus_eur = Bonus.objects.create(
            money_type='EUR',
            amount=10,
            event='DEPOSIT',
            deposit_min_value=20,
            wagering_requirement=20
        )

        self.deposit_bonus_bns = Bonus.objects.create(
            money_type='BNS',
            amount=20,
            event='DEPOSIT',
            deposit_min_value=100,
            wagering_requirement=20
        )

    def test_deposit_money_amount_lt_bonus_min_deposit(self):
        # Money amount less then min deposit specified in all bonusses
        deposit_done.send(sender=None, user=self.user, amount=10)
        wallet_eur = self.user.player.get_or_create_wallet(money_type='EUR')
        wallet_bns = self.user.player.get_or_create_wallet(money_type='BNS')
        self.assertEqual(wallet_eur.balance, 0)
        self.assertEqual(wallet_bns.balance, 0)

    def test_deposit_money_amount_between_bonus_min_deposit(self):
        # Money amount between eur bonus and bns bonus
        deposit_done.send(sender=None, user=self.user, amount=30)
        wallet_eur = self.user.player.get_or_create_wallet(money_type='EUR')
        wallet_bns = self.user.player.get_or_create_wallet(money_type='BNS')
        self.assertEqual(wallet_eur.balance, 10)
        self.assertEqual(wallet_bns.balance, 0)

    def test_deposit_money_amount_gt_bonus_min_deposit(self):
        # Money amount greater then min deposit specified in all bonusses
        deposit_done.send(sender=None, user=self.user, amount=110)
        wallet_eur = self.user.player.get_or_create_wallet(money_type='EUR')
        wallet_bns = self.user.player.get_or_create_wallet(money_type='BNS')
        self.assertEqual(wallet_eur.balance, 10)
        self.assertEqual(wallet_bns.balance, 20)
        wag_req_list = WageringRequirement.objects.filter(
            user=self.user,
            wallet=wallet_bns,
            bonus=self.deposit_bonus_bns,
            is_active=True
        )

        self.assertEqual(len(wag_req_list), 1)
        wallet_eur.delete()
        wallet_bns.delete()


class BonusOnLoginHandlerTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username='test1',
            password='Password1'
        )

    def test_first_login_bonus_eur(self):
        first_login_bonus = Bonus.objects.create(
            money_type='EUR',
            amount=100,
            event='FIRST_LOGIN'
        )
        self.assertEqual(self.user.player.is_login_bonus_used, False)
        self.client.force_login(self.user)
        wallet_eur = self.user.player.get_or_create_wallet(money_type='EUR')
        self.assertEqual(wallet_eur.balance, 100)
        self.assertEqual(self.user.player.is_login_bonus_used, True)
        self.client.logout()
        self.client.force_login(self.user)
        wallet_eur = self.user.player.get_or_create_wallet(money_type='EUR')
        self.assertEqual(wallet_eur.balance, 100)
        wallet_eur.delete()

    def test_login_bonus_eur(self):
        login_bonus = Bonus.objects.create(
            money_type='EUR',
            amount=120,
            event='LOGIN'
        )
        self.client.force_login(self.user)
        wallet_eur = self.user.player.get_or_create_wallet(money_type='EUR')
        self.assertEqual(wallet_eur.balance, 120)
        self.client.logout()
        self.client.force_login(self.user)
        wallet_eur = self.user.player.get_or_create_wallet(money_type='EUR')
        self.assertEqual(wallet_eur.balance, 240)
        wallet_eur.delete()

    def test_login_bonus_bns(self):
        login_bonus = Bonus.objects.create(
            money_type='BNS',
            amount=30,
            event='LOGIN'
        )
        self.client.force_login(self.user)
        try:
            wallet = Wallet.objects.get(owner=self.user, money_type='BNS', is_depleted=False)
        except ObjectDoesNotExist:
            self.fail("Wallet does not exist!")
        self.assertEqual(wallet.balance, 30)
        self.client.logout()
        self.client.force_login(self.user)
        wallet = Wallet.objects.get(pk=wallet.pk)
        self.assertEqual(wallet.balance, 60)
        wallet.delete()
