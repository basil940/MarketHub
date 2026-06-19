from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user):
    subject = 'Welcome to MarketHub! 🎉'
    message = f'''
Hi {user.username},

Welcome to MarketHub! We're excited to have you on board.

Start shopping now at http://127.0.0.1:8000/

You'll earn loyalty points on every purchase:
- 20 points per ₹100 spent
- 1 point = ₹2 discount on future orders

Happy Shopping!
Team MarketHub
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True
    )


def send_order_confirmation_email(order):
    items_text = '\n'.join([
        f'  • {item.product_name} x{item.quantity} — ₹{item.subtotal()}'
        for item in order.items.all()
    ])

    subject = f'Order Confirmed — Order #{order.id} 📦'
    message = f'''
Hi {order.user.username},

Thank you for your order! Here are your order details:

Order ID: #{order.id}
Status: {order.get_status_display()}

Items:
{items_text}

Total Amount: ₹{order.total_amount}
Delivery Address: {order.shipping_address}

You can track your order at:
http://127.0.0.1:8000/orders/

Thank you for shopping with MarketHub!
Team MarketHub
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=True
    )


def send_payment_confirmation_email(order, points_earned):
    items_text = '\n'.join([
        f'  • {item.product_name} x{item.quantity} — ₹{item.subtotal()}'
        for item in order.items.all()
    ])

    subject = f'Payment Successful — Order #{order.id} ✅'
    message = f'''
Hi {order.user.username},

Your payment was successful! 🎉

Order ID: #{order.id}
Items:
{items_text}

Total Paid: ₹{order.total_amount}
Payment Status: Paid ✅

🎁 You earned {points_earned} loyalty points for this order!

Track your order at:
http://127.0.0.1:8000/orders/

Thank you for shopping with MarketHub!
Team MarketHub
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=True
    )


def send_cancellation_email(order):
    subject = f'Order #{order.id} Cancelled'
    message = f'''
Hi {order.user.username},

Your order #{order.id} has been cancelled successfully.

Total Amount: ₹{order.total_amount}
Delivery Address: {order.shipping_address}

If you cancelled by mistake, you can place a new order at:
http://127.0.0.1:8000/

If you have any questions, please contact us.

Team MarketHub
'''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=True
    )