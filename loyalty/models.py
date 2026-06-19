from django.db import models
from django.conf import settings


class LoyaltyAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loyalty')
    points = models.PositiveIntegerField(default=0)
    total_earned = models.PositiveIntegerField(default=0)
    total_redeemed = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.points} points"


class LoyaltyTransaction(models.Model):
    TYPE_CHOICES = [
        ('earned',   'Earned'),
        ('redeemed', 'Redeemed'),
        ('refunded', 'Refunded'),
    ]

    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    points = models.IntegerField()  # positive = earned, negative = redeemed
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account.user.username} — {self.type} {self.points} pts"

    class Meta:
        ordering = ['-created_at']