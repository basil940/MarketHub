from django.urls import path
from .views import LoyaltyAccountView, RedeemPointsView

urlpatterns = [
    path('', LoyaltyAccountView.as_view(), name='loyalty-account'),
    path('redeem/', RedeemPointsView.as_view(), name='redeem-points'),
]