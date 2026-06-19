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
        try:
            range_days = int(request.query_params.get('range', 7))
        except (TypeError, ValueError):
            range_days = 7
        if range_days not in (7, 30, 90):
            range_days = 7

        start_date = today - timedelta(days=range_days - 1)
        prev_start = start_date - timedelta(days=range_days)
        prev_end = start_date - timedelta(days=1)

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

        current_revenue = Order.objects.filter(
            payment_status='paid',
            created_at__date__range=(start_date, today)
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        range_orders = Order.objects.filter(
            created_at__date__range=(start_date, today)
        ).count()

        previous_revenue = Order.objects.filter(
            payment_status='paid',
            created_at__date__range=(prev_start, prev_end)
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        comparison_revenue = float(current_revenue) - float(previous_revenue)
        if previous_revenue:
            comparison_pct = (comparison_revenue / float(previous_revenue)) * 100
        else:
            comparison_pct = 0.0

        revenue_chart = []
        for i in range(range_days - 1, -1, -1):
            day = today - timedelta(days=i)
            rev = Order.objects.filter(
                created_at__date=day,
                payment_status='paid'
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            revenue_chart.append({
                'date': day.strftime('%d %b'),
                'revenue': float(rev)
            })

        top_products = OrderItem.objects.values(
            'product_name'
        ).annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('product_price') * F('quantity'))
        ).order_by('-total_qty')[:5]

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
            'range_days': range_days,
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'total_users': total_users,
            'orders_today': orders_today,
            'revenue_today': float(revenue_today),
            'pending_orders': pending_orders,
            'range_revenue': float(current_revenue),
            'range_orders': range_orders,
            'comparison_revenue': comparison_revenue,
            'comparison_pct': round(comparison_pct, 1),
            'revenue_chart': revenue_chart,
            'top_products': list(top_products),
            'recent_orders': recent_list,
        })
