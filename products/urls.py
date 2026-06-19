from django.urls import path
from .views import (
    CategoryListView, ProductListView,
    ProductDetailView, InventoryUpdateView,
    ProductReviewView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('', ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('<slug:slug>/inventory/', InventoryUpdateView.as_view(), name='inventory-update'),
    path('<slug:slug>/reviews/', ProductReviewView.as_view(), name='product-reviews'),
]