from django.test import TestCase
from django.contrib.auth.models import User
from player.models import Bonus, Wallet, WageringRequirement, Player
from igaming import utils


class PlayerModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test1',
            password='Password1'
        )

        self.deposit_bonus = Bonus.objects.create(
            money_type='BNS',
            amount=20,
            event='DEPOSIT',
            deposit_min_value=100,
            wagering_requirement=20
        )

    def test_player_created(self):
        test_user = User.objects.create(
            username='test2',
            password='Password2'
        )
        self.assertIsNotNone(test_user.player)

    def test_set_spin_result_lose_all(self):
        wallet = Wallet.objects.create(
            owner=self.user,
            balance=utils.BET_VALUE,
            money_type='BNS'
        )
        wallet.set_spin_result(0)
        self.assertEqual(wallet.balance, 0)
        self.assertEqual(wallet.is_depleted, True)

    def test_update_wag_req_not_enough_money_to_withdraw_wallet_depleted(self):
        self.user.player.money_wagered = 400
        self.user.player.save()

        bonus_wallet = Wallet.objects.create(
            money_type='BNS',
            balance=10,
            owner=self.user
        )

        real_wallet = Wallet.objects.create(
            money_type='EUR',
            balance=10,
            owner=self.user
        )

        wag_req = WageringRequirement.objects.create(
            bonus=self.deposit_bonus,
            user=self.user,
            wallet=bonus_wallet,
            is_active=True
        )

        self.user.player.update_wagering_requirement()

        self.assertEqual(Wallet.objects.get(pk=bonus_wallet.pk).balance, 0)
        self.assertEqual(Wallet.objects.get(pk=bonus_wallet.pk).is_depleted, True)
        self.assertEqual(Wallet.objects.get(pk=real_wallet.pk).balance, 20)
        self.assertEqual(Player.objects.get(pk=self.user.player.pk).money_wagered, utils.BET_VALUE)
        self.assertEqual(WageringRequirement.objects.get(pk=wag_req.pk).is_active, False)

    def test_update_wag_req_enough_money_to_withdraw_wallet_not_depleted(self):
        self.user.player.money_wagered = 400
        self.user.player.save()

        bonus_wallet = Wallet.objects.create(
            money_type='BNS',
            balance=40,
            owner=self.user
        )

        real_wallet = Wallet.objects.create(
            money_type='EUR',
            balance=10,
            owner=self.user
        )

        wag_req = WageringRequirement.objects.create(
            bonus=self.deposit_bonus,
            user=self.user,
            wallet=bonus_wallet,
            is_active=True
        )

        self.user.player.update_wagering_requirement()

        self.assertEqual(Wallet.objects.get(pk=real_wallet.pk).balance, 30)
        self.assertEqual(Wallet.objects.get(pk=bonus_wallet.pk).is_depleted, False)
        self.assertEqual(Wallet.objects.get(pk=bonus_wallet.pk).balance, 20)
        self.assertEqual(Player.objects.get(pk=self.user.player.pk).money_wagered, utils.BET_VALUE)
        self.assertEqual(WageringRequirement.objects.get(pk=wag_req.pk).is_active, False)


class WalletModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='test1',
            password='Password1'
        )

    def test_set_spin_result_win(self):
        wallet = Wallet.objects.create(
            owner=self.user,
            balance=10,
            money_type='BNS'
        )
        wallet.set_spin_result(1)
        self.assertEqual(wallet.balance, 10 + utils.WIN_VALUE)
        self.assertEqual(wallet.is_depleted, False)

    def test_set_spin_result_lose(self):
        wallet = Wallet.objects.create(
            owner=self.user,
            balance=10,
            money_type='BNS'
        )
        wallet.set_spin_result(0)
        self.assertEqual(wallet.balance, 10 - utils.BET_VALUE)
        self.assertEqual(wallet.is_depleted, False)

    def test_save_new_wallet_priority(self):
        wallet1 = Wallet.objects.create(
            owner=self.user,
            balance=10,
            money_type='BNS'
        )

        self.assertEqual(wallet1.spin_priority, 2)

        wallet2 = Wallet.objects.create(
            owner=self.user,
            balance=10,
            money_type='OTHER'
        )

        self.assertEqual(wallet2.spin_priority, 3)

        wallet3 = Wallet.objects.create(
            owner=self.user,
            balance=10,
            money_type='EUR'
        )

        self.assertEqual(wallet3.spin_priority, 1)

    def test_save_existing_wallet_priority(self):
        wallet = Wallet.objects.create(
            owner=self.user,
            balance=10,
            money_type='BNS'
        )

        wallet.spin_priority = 3
        wallet.save()
        self.assertEqual(wallet.spin_priority, 3)
