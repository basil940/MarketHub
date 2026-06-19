from django.urls import path
from .views import WishlistView, WishlistToggleView, WishlistStatusView

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist'),
    path('toggle/<int:product_id>/', WishlistToggleView.as_view(), name='wishlist-toggle'),
    path('status/<int:product_id>/', WishlistStatusView.as_view(), name='wishlist-status'),
]