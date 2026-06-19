from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('confirmed',   'Confirmed'),
        ('processing',  'Processing'),
        ('shipped',     'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered',   'Delivered'),
        ('cancelled',   'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid',   'Unpaid'),
        ('paid',     'Paid'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_intent_id = models.CharField(max_length=200, blank=True)
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} — {self.status}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def subtotal(self):
        return self.product_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    note = models.CharField(max_length=300, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.id} → {self.status}"

    class Meta:
        ordering = ['-updated_at']