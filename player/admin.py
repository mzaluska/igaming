from django.contrib import admin
from .models import Wallet, Player, Bonus, WageringRequirement
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = 'Player'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (PlayerInline, )

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


class BonusAdmin(admin.ModelAdmin):
    list_display = ["event", "money_type", "amount", "deposit_min_value", "wagering_requirement"]
    list_filter = ["event", "money_type"]


class WalletAdmin(admin.ModelAdmin):
    list_display = ["owner", "money_type", "balance", "is_depleted", "spin_priority"]
    list_filter = ["owner", "is_depleted"]
    ordering = ('is_depleted',)

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("spin_priority",)
        form = super(WalletAdmin, self).get_form(request, obj, **kwargs)
        return form


class WageringRequirementAdmin(admin.ModelAdmin):
    list_display = ["wallet", "__str__", "is_active"]
    list_editable = ["is_active"]
    list_filter = ["bonus", "is_active"]
    ordering = ('is_active',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Bonus, BonusAdmin)
admin.site.register(Wallet, WalletAdmin)
admin.site.register(WageringRequirement, WageringRequirementAdmin)
