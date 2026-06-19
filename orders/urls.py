from django.urls import path
from .views import (
    PlaceOrderView, OrderListView,
    OrderDetailView, CancelOrderView,
    UpdateOrderStatusView, AdminOrderListView,
    CreateCheckoutSessionView, StripeWebhookView
)

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('place/', PlaceOrderView.as_view(), name='place-order'),
    path('admin/', AdminOrderListView.as_view(), name='admin-order-list'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
    path('<int:order_id>/status/', UpdateOrderStatusView.as_view(), name='update-status'),
    path('<int:order_id>/checkout/', CreateCheckoutSessionView.as_view(), name='checkout'),
]