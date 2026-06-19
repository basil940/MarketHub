from rest_framework import serializers
from .models import LoyaltyAccount, LoyaltyTransaction


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'type', 'points', 'description', 'created_at']


class LoyaltyAccountSerializer(serializers.ModelSerializer):
    transactions = LoyaltyTransactionSerializer(many=True, read_only=True)
    points_value = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyAccount
        fields = ['points', 'total_earned', 'total_redeemed', 'points_value', 'transactions', 'updated_at']

    def get_points_value(self, obj):
        return obj.points * 2  # 1 point = ₹2