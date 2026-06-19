from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import Category, Product, Inventory, Review
from .serializers import (
    CategorySerializer, ProductSerializer,
    ProductCreateSerializer, InventorySerializer, ReviewSerializer
)
from products import models


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListView(APIView):
    def get(self, request):
        products = Product.objects.filter(is_active=True).select_related('category', 'inventory')

        search = request.query_params.get('search')
        if search:
            products = products.filter(name__icontains=search)

        category = request.query_params.get('category')
        if category:
            products = products.filter(category__slug=category)

        sort = request.query_params.get('sort')
        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
        elif sort == 'newest':
            products = products.order_by('-created_at')

        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        return Response(ProductSerializer(product).data)

    def put(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductCreateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        product.is_active = False
        product.save()
        return Response({'message': 'Product deactivated'}, status=status.HTTP_200_OK)


class InventoryUpdateView(APIView):
    def patch(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        inventory = get_object_or_404(Inventory, product=product)
        serializer = InventorySerializer(inventory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductReviewView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # public
        return [IsAuthenticated()]

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        reviews = product.reviews.all()
        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        from orders.models import Order
        has_purchased = Order.objects.filter(
            user=request.user,
            status='delivered',
            items__product=product
        ).exists()

        if not has_purchased:
            return Response(
                {'error': 'You can only review products you have purchased and received.'},
                status=status.HTTP_403_FORBIDDEN
            )

        existing = Review.objects.filter(product=product, user=request.user).first()
        if existing:
            serializer = ReviewSerializer(existing, data=request.data, partial=True)
        else:
            serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            rating = serializer.validated_data.get('rating')
            if not (1 <= rating <= 5):
                return Response({'error': 'Rating must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(product=product, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        review = get_object_or_404(Review, product=product, user=request.user)
        review.delete()
        return Response({'message': 'Review deleted'})


from orders.models import Order

class AdminStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_products = Product.objects.filter(is_active=True).count()
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        revenue = Order.objects.exclude(status='cancelled').aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0

        return Response({
            'total_products': total_products,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': revenue,
        })