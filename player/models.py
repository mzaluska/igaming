from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import MultipleObjectsReturned
from igaming import utils


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_login_bonus_used = models.BooleanField(default=False, verbose_name='Login bonus used')
    money_wagered = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    def get_all_wallets(self):
        # all user wallets ordered by spin priority
        return Wallet.objects.filter(
            owner=self.user,
            is_depleted=False
        ).order_by('spin_priority')

    def get_or_create_wallet(self, money_type):
        # User wallet for proper money type
        try:
            wallet, created = Wallet.objects.get_or_create(
                owner=self.user,
                is_depleted=False,
                money_type=money_type
            )
        except MultipleObjectsReturned:
            wallet = Wallet.objects.filter(
                owner=self.user,
                is_depleted=False,
                money_type=money_type
            )[0]
        return wallet

    def get_money_left_to_withdrawal(self):
        # Counts how much money left to withdraw bonus money
        requirements = WageringRequirement.objects.filter(
            user=self.user,
            is_active=True,
            bonus__is_active=True
        ).order_by('created_at')

        if len(requirements) > 0:
            return round(requirements[0].get_wagering_requirement() - self.money_wagered, 2)
        else:
            return 0

    def update_wagering_requirement(self):
        # Get first active wagering requirements created for user money by getting bonus
        # Move bonus money to real wallet and removes WageringRequirement because it's used

        requirements = WageringRequirement.objects.filter(
            user=self.user,
            is_active=True,
            bonus__is_active=True
        ).order_by('created_at')

        if len(requirements) == 0:
            return True

        req = requirements[0]

        # Counting player money wagered only if there exists possibility, to withdrawal
        # (only if WageringRequirement exists)
        self.money_wagered = self.money_wagered + utils.BET_VALUE

        if req.get_wagering_requirement() <= self.money_wagered:
            # When there is enough money wagered and wallet balance is enough to withdraw
            # 1. decrease the money wagered counter on player object
            # 2. convert bonus money to real money
            # 3. set object WageringRequirement to inactive
            # 4. save changes on each object

            # When wallet balance is too low then withdraw only the rest
            withdrawal = req.bonus.amount
            if req.wallet.balance < req.bonus.amount:
                withdrawal = req.wallet.balance
            self.money_wagered = self.money_wagered - req.get_wagering_requirement()
            real_wallet = self.get_or_create_wallet(money_type='EUR')
            real_wallet.balance = real_wallet.balance + withdrawal
            req.wallet.balance = req.wallet.balance - withdrawal

            if req.wallet.balance == 0:
                req.wallet.is_depleted = True
            req.is_active = False
            req.save()
            req.wallet.save()
            real_wallet.save()

        self.save()

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_player(sender, instance, created, **kwargs):
    # Creates player after saving user
    if created:
        profile, new = Player.objects.get_or_create(user=instance)


class Wallet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_depleted = models.BooleanField(default=False)
    money_type = models.CharField(max_length=3, default='BNS', choices=utils.MONEY_TYPES)
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    spin_priority = models.IntegerField(default=1)

    def set_spin_result(self, result):
        self.balance = self.balance - utils.BET_VALUE
        if result == 1:
            # Player won
            self.balance = self.balance + utils.BET_VALUE + utils.WIN_VALUE
        else:
            # Player lost
            if self.balance == 0:
                self.is_depleted = True
        self.save()

    def save(self, *args, **kwargs):
        # sets spin priority automaticcaly for wallet
        if self.pk is None:
            if self.money_type == 'EUR':
                self.spin_priority = 1
            elif self.money_type == 'BNS':
                self.spin_priority = 2
            else:
                self.spin_priority = 3
        super(Wallet, self).save(*args, **kwargs)

    def __str__(self):
        return 'owner: ' + self.owner.username + ', money type:' + self.get_money_type_display()


class Bonus(models.Model):
    money_type = models.CharField(max_length=3, default='BNS', choices=utils.MONEY_TYPES)
    is_active = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    event = models.CharField(max_length=20, default='FIRST_LOGIN', choices=utils.BONUS_EVENTS)
    deposit_min_value = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    wagering_requirement = models.DecimalField(max_digits=16, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'Bonus'

    def __str__(self):
        return 'Bonus on: ' + self.get_event_display() + \
               ', amount: ' + str(self.amount) + \
               ' ' + self.get_money_type_display()


class WageringRequirement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    bonus = models.ForeignKey(Bonus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def get_wagering_requirement(self):
        return self.bonus.amount * self.bonus.wagering_requirement

    def __str__(self):
        return 'Money to withdraw: ' + str(self.bonus.amount) + \
               ', requirement: ' + str(round(self.get_wagering_requirement(), 2))
