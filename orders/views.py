from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Order, OrderItem, OrderTracking
from .serializers import OrderSerializer, PlaceOrderSerializer, OrderTrackingSerializer
from cart.models import Cart
import stripe
from decimal import Decimal
from dashboard.utils import broadcast_dashboard
from ecomsite.emails import (
    send_order_confirmation_email,
    send_payment_confirmation_email,
    send_cancellation_email
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class PlaceOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.select_related('product__inventory').all()
        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.product.inventory.stock < item.quantity:
                return Response(
                    {'error': f'Not enough stock for {item.product.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        total = sum(item.product.discounted_price() * item.quantity for item in cart_items)

        # Apply loyalty points discount
        redeem_points = serializer.validated_data.get('redeem_points', 0)
        discount_from_points = 0

        if redeem_points > 0:
            from loyalty.models import LoyaltyAccount, LoyaltyTransaction
            try:
                account = LoyaltyAccount.objects.get(user=request.user)
                if redeem_points > account.points:
                    return Response(
                        {'error': f'Not enough points. You have {account.points} points.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                max_discount = total * Decimal('0.5')
                discount_from_points = min(Decimal(redeem_points * 2), max_discount)
                total = total - discount_from_points

            except LoyaltyAccount.DoesNotExist:
                redeem_points = 0

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data['shipping_address'],
            total_amount=total,
            status='pending',
            payment_status='unpaid'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.discounted_price(),
                quantity=item.quantity
            )
            inventory = item.product.inventory
            inventory.stock -= item.quantity
            inventory.save()

        # Deduct redeemed points
        if redeem_points > 0:
            account.points -= redeem_points
            account.total_redeemed += redeem_points
            account.save()

            LoyaltyTransaction.objects.create(
                account=account,
                type='redeemed',
                points=-redeem_points,
                description=f'Redeemed for Order #{order.id} (₹{discount_from_points} discount)'
            )

        OrderTracking.objects.create(
            order=order,
            status='pending',
            note='Order placed, awaiting payment'
        )

        cart.items.all().delete()

        # Broadcast new order event
        broadcast_dashboard('new_order', {
            'order_id': order.id,
            'amount': str(order.total_amount),
            'username': order.user.username,
        })

        # Send order confirmation email
        if order.user.email:
            send_order_confirmation_email(order)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_status == 'paid':
            return Response({'error': 'Order already paid'}, status=status.HTTP_400_BAD_REQUEST)

        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': item.product_name,
                    },
                    'unit_amount': int(item.product_price * 100),
                },
                'quantity': item.quantity,
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'http://127.0.0.1:8000/orders/?payment=success&order_id={order.id}',
            cancel_url=f'http://127.0.0.1:8000/orders/?payment=cancelled&order_id={order.id}',
            metadata={'order_id': order.id}
        )

        order.payment_intent_id = checkout_session.id
        order.save()

        return Response({'checkout_url': checkout_session.url})


class StripeWebhookView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            order_id = session['metadata']['order_id']

            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'paid'
                order.status = 'confirmed'
                order.save()

                OrderTracking.objects.create(
                    order=order,
                    status='confirmed',
                    note='Payment successful via Stripe'
                )

                # Award loyalty points
                from loyalty.models import LoyaltyAccount, LoyaltyTransaction
                account, _ = LoyaltyAccount.objects.get_or_create(user=order.user)
                points_earned = int(order.total_amount / 100 * 20)

                if points_earned > 0:
                    account.points += points_earned
                    account.total_earned += points_earned
                    account.save()

                    LoyaltyTransaction.objects.create(
                        account=account,
                        type='earned',
                        points=points_earned,
                        description=f'Earned for Order #{order.id} (₹{order.total_amount})'
                    )

                # Broadcast payment confirmed event
                broadcast_dashboard('payment_confirmed', {
                    'order_id': order.id,
                    'amount': str(order.total_amount),
                    'username': order.user.username,
                })

                # Send payment confirmation email
                if order.user.email:
                    send_payment_confirmation_email(order, points_earned)

            except Order.DoesNotExist:
                pass

        return Response({'status': 'ok'})


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return Response(OrderSerializer(orders, many=True).data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return Response(OrderSerializer(order).data)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in ['shipped', 'out_for_delivery', 'delivered']:
            return Response(
                {'error': f'Cannot cancel order in {order.status} status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in order.items.all():
            if item.product:
                inventory = item.product.inventory
                inventory.stock += item.quantity
                inventory.save()

        order.status = 'cancelled'
        order.save()

        OrderTracking.objects.create(
            order=order,
            status='cancelled',
            note='Order cancelled by user'
        )

        # Send cancellation email
        if order.user.email:
            send_cancellation_email(order)

        return Response({'message': 'Order cancelled successfully'})


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status')
        note = request.data.get('note', '')

        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Choose from {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        OrderTracking.objects.create(
            order=order,
            status=new_status,
            note=note
        )

        return Response(OrderSerializer(order).data)


class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')
        return Response(OrderSerializer(orders, many=True).data)