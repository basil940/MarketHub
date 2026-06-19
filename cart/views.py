from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    # Get cart
    def get(self, request):
        cart = get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)

    # Add item to cart
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id, is_active=True)

        # Check stock
        if product.inventory.stock < quantity:
            return Response(
                {'error': f'Only {product.inventory.stock} units available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = get_or_create_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    # Clear entire cart
    def delete(self, request):
        cart = get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    # Update quantity
    def patch(self, request, item_id):
        cart = get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.data.get('quantity', 1))

        if quantity <= 0:
            item.delete()
            return Response({'message': 'Item removed'}, status=status.HTTP_200_OK)

        if item.product.inventory.stock < quantity:
            return Response(
                {'error': f'Only {item.product.inventory.stock} units available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = quantity
        item.save()
        return Response(CartSerializer(cart).data)

    # Remove single item
    def delete(self, request, item_id):
        cart = get_or_create_cart(request.user)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)