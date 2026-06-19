from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import WishlistItem
from .serializers import WishlistItemSerializer
from products.models import Product


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    # Get all wishlist items
    def get(self, request):
        items = WishlistItem.objects.filter(user=request.user).select_related('product')
        return Response(WishlistItemSerializer(items, many=True).data)


class WishlistToggleView(APIView):
    permission_classes = [IsAuthenticated]

    # Add or remove — toggle
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            item.delete()
            return Response({'status': 'removed', 'message': f'{product.name} removed from wishlist'})

        return Response({'status': 'added', 'message': f'{product.name} added to wishlist'}, status=status.HTTP_201_CREATED)


class WishlistStatusView(APIView):
    permission_classes = [IsAuthenticated]

    # Check if a product is in wishlist
    def get(self, request, product_id):
        exists = WishlistItem.objects.filter(user=request.user, product_id=product_id).exists()
        return Response({'in_wishlist': exists})