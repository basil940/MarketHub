from django.contrib import admin
from .models import Order, OrderItem, OrderTracking


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'quantity']


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_amount', 'created_at']
    list_filter = ['status']
    search_fields = ['user__username']
    inlines = [OrderItemInline, OrderTrackingInline]


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'note', 'updated_at']