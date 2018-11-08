from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import DepositForm
from player.signals import deposit_done
from player.models import Wallet
from igaming import utils
import random


@login_required
def home(request):
    if request.method == 'POST':
        wallets = request.user.player.get_all_wallets()
        # Spin button - check if there's enough money and sets the game result
        for wallet in wallets:
            if wallet.balance < utils.BET_VALUE:
                message = 'Not enough money'
                continue
            else:
                play_result = random.randint(0, 1)
                wallet.set_spin_result(play_result)
                if play_result == 1:
                    message = 'You won!'
                else:
                    message = 'You lost!'
                request.user.player.update_wagering_requirement()
                break
    else:
        message = 'Play a game!'

    wallets = request.user.player.get_all_wallets()
    money_left = request.user.player.get_money_left_to_withdrawal()
    context = {
        'wallets': wallets,
        'bet': utils.BET_VALUE,
        'message': message,
        'money_left': money_left
    }
    return render(request, 'player/home.html', context)


@login_required
def deposit_money(request):
    # Deposit - increase real wallet balance
    if request.method == "POST":
        wallet = request.user.player.get_or_create_wallet('EUR')
        form = DepositForm(data=request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            wallet.balance = wallet.balance + amount
            wallet.save()
            # signal to give a bonus on deposit
            deposit_done.send(sender=None, user=request.user, amount=amount)
            return redirect('player_home')
    else:
        form = DepositForm()
    return render(request, 'player/deposit_form.html', {'form': form})


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'player/signup_form.html'
    success_url = reverse_lazy('player_home')