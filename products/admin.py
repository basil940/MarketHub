from django.contrib import admin
from .models import Category, Product, Inventory, Review


class InventoryInline(admin.TabularInline):
    model = Inventory
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_percent', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [InventoryInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'stock', 'last_updated']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']
    search_fields = ['product__name', 'user__username']