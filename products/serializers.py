from rest_framework import serializers
from .models import Category, Product, Inventory, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['stock', 'last_updated']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'username', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discounted_price = serializers.SerializerMethodField()
    inventory = InventorySerializer(read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'discount_percent', 'discounted_price',
            'image', 'is_active', 'category', 'category_name',
            'inventory', 'created_at', 'avg_rating', 'review_count'
        ]

    def get_discounted_price(self, obj):
        return obj.discounted_price()

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    def get_review_count(self, obj):
        return obj.reviews.count()


class ProductCreateSerializer(serializers.ModelSerializer):
    stock = serializers.IntegerField(write_only=True, default=0)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'price', 'discount_percent', 'image',
            'is_active', 'category', 'stock'
        ]

    def create(self, validated_data):
        stock = validated_data.pop('stock', 0)
        product = Product.objects.create(**validated_data)
        Inventory.objects.create(product=product, stock=stock)
        return product