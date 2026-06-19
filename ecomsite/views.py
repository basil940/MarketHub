from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, F

User = get_user_model()


class DashboardStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now().date()
        last_7_days = timezone.now() - timedelta(days=7)

        # Overall stats
        total_revenue = Order.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        total_orders = Order.objects.count()
        total_users = User.objects.count()

        orders_today = Order.objects.filter(
            created_at__date=today
        ).count()

        revenue_today = Order.objects.filter(
            created_at__date=today,
            payment_status='paid'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        pending_orders = Order.objects.filter(status='pending').count()

        # Revenue last 7 days
        revenue_chart = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            rev = Order.objects.filter(
                created_at__date=day,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            revenue_chart.append({
                'date': day.strftime('%d %b'),
                'revenue': float(rev)
            })

        # Top 5 products by quantity sold
        top_products = OrderItem.objects.values(
            'product_name'
        ).annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('product_price') * F('quantity'))
        ).order_by('-total_qty')[:5]

        # Recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        recent_list = [{
            'id': o.id,
            'username': o.user.username,
            'amount': str(o.total_amount),
            'status': o.status,
            'payment_status': o.payment_status,
            'created_at': o.created_at.strftime('%d %b, %H:%M')
        } for o in recent_orders]

        return Response({
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'total_users': total_users,
            'orders_today': orders_today,
            'revenue_today': float(revenue_today),
            'pending_orders': pending_orders,
            'revenue_chart': revenue_chart,
            'top_products': list(top_products),
            'recent_orders': recent_list,
        })