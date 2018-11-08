from .models import Bonus, WageringRequirement
from player.signals import deposit_done
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(deposit_done)
def set_user_bonus_on_deposit(sender, user, amount, **kwargs):
    # Increase wallet balance on deposit if bonus exists and add wagering requirement
    bonus_list = Bonus.objects.filter(event='DEPOSIT', is_active=True)

    for bonus in bonus_list:
        if bonus.deposit_min_value < amount:
            wallet = user.player.get_or_create_wallet(money_type=bonus.money_type)
            wallet.balance = wallet.balance + bonus.amount
            wallet.save()

            if bonus.money_type == 'BNS':
                wagering_req = WageringRequirement(
                    user=user,
                    wallet=wallet,
                    bonus=bonus,
                    is_active=True
                )

                wagering_req.save()


@receiver(user_logged_in)
def set_user_bonus_on_login(sender, user, request, **kwargs):

    bonus_list = Bonus.objects.filter(event__contains='LOGIN', is_active=True)

    for bonus in bonus_list:
        if bonus.event == 'FIRST_LOGIN':
            if user.player.is_login_bonus_used:
                continue
            user.player.is_login_bonus_used = True
            user.player.save()
        wallet = user.player.get_or_create_wallet(money_type=bonus.money_type)
        wallet.balance = wallet.balance + bonus.amount
        wallet.save()

