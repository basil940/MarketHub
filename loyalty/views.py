from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import LoyaltyAccount, LoyaltyTransaction
from .serializers import LoyaltyAccountSerializer


def get_or_create_account(user):
    account, _ = LoyaltyAccount.objects.get_or_create(user=user)
    return account


class LoyaltyAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = get_or_create_account(request.user)
        return Response(LoyaltyAccountSerializer(account).data)


class RedeemPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        points_to_redeem = int(request.data.get('points', 0))
        account = get_or_create_account(request.user)

        if points_to_redeem <= 0:
            return Response({'error': 'Invalid points amount'}, status=status.HTTP_400_BAD_REQUEST)

        if points_to_redeem > account.points:
            return Response({'error': f'Not enough points. You have {account.points} points.'}, status=status.HTTP_400_BAD_REQUEST)

        discount = points_to_redeem * 2  # 1 point = ₹2

        return Response({
            'points_to_redeem': points_to_redeem,
            'discount_amount': discount,
            'remaining_points': account.points - points_to_redeem
        })