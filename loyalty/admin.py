from django.contrib import admin
from .models import LoyaltyAccount, LoyaltyTransaction


class LoyaltyTransactionInline(admin.TabularInline):
    model = LoyaltyTransaction
    extra = 0
    readonly_fields = ['type', 'points', 'description', 'created_at']


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'total_earned', 'total_redeemed', 'updated_at']
    inlines = [LoyaltyTransactionInline]


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'type', 'points', 'description', 'created_at']