from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/products/', include('products.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/wishlist/', include('wishlist.urls')),
    path('api/loyalty/', include('loyalty.urls')),
    path('api/dashboard/', include('dashboard.urls')),

    # Frontend pages
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('product/', TemplateView.as_view(template_name='product.html'), name='product'),
    path('cart/', TemplateView.as_view(template_name='cart.html'), name='cart'),
    path('orders/', TemplateView.as_view(template_name='orders.html'), name='orders'),
    path('wishlist/', TemplateView.as_view(template_name='wishlist.html'), name='wishlist'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)