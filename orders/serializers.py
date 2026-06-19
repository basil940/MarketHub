from rest_framework import serializers
from .models import Order, OrderItem, OrderTracking


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTracking
        fields = ['id', 'status', 'note', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking = OrderTrackingSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'shipping_address',
            'total_amount', 'items', 'tracking', 'created_at', 'updated_at',
            'payment_status', 'payment_status_display', 'payment_intent_id'
        ]


class PlaceOrderSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    redeem_points = serializers.IntegerField(default=0, min_value=0)