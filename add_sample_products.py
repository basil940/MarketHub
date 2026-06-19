"""
Run this script to populate the database with sample products:
python manage.py shell < add_sample_products.py
"""

from products.models import Category, Product, Inventory

# Clear existing data
Category.objects.all().delete()
Product.objects.all().delete()

# Create categories
electronics = Category.objects.create(name='Electronics', slug='electronics')
clothing = Category.objects.create(name='Clothing', slug='clothing')
home = Category.objects.create(name='Home & Kitchen', slug='home-kitchen')

# Create sample products
products_data = [
    # Electronics
    {
        'name': 'Wireless Headphones',
        'slug': 'wireless-headphones',
        'category': electronics,
        'price': 2999,
        'discount_percent': 20,
        'description': 'Premium wireless headphones with noise cancellation',
        'stock': 15,
    },
    {
        'name': 'USB-C Charger',
        'slug': 'usb-c-charger',
        'category': electronics,
        'price': 899,
        'discount_percent': 10,
        'description': 'Fast charging USB-C charger for all devices',
        'stock': 30,
    },
    {
        'name': 'Laptop Stand',
        'slug': 'laptop-stand',
        'category': electronics,
        'price': 1499,
        'discount_percent': 15,
        'description': 'Adjustable aluminum laptop stand',
        'stock': 20,
    },
    # Clothing
    {
        'name': 'Cotton T-Shirt',
        'slug': 'cotton-t-shirt',
        'category': clothing,
        'price': 499,
        'discount_percent': 25,
        'description': 'Premium quality 100% cotton t-shirt',
        'stock': 50,
    },
    {
        'name': 'Jeans',
        'slug': 'jeans',
        'category': clothing,
        'price': 1299,
        'discount_percent': 30,
        'description': 'Comfortable and stylish denim jeans',
        'stock': 40,
    },
    # Home & Kitchen
    {
        'name': 'Coffee Maker',
        'slug': 'coffee-maker',
        'category': home,
        'price': 3999,
        'discount_percent': 20,
        'description': 'Automatic coffee maker with timer',
        'stock': 12,
    },
    {
        'name': 'Kitchen Knife Set',
        'slug': 'kitchen-knife-set',
        'category': home,
        'price': 2499,
        'discount_percent': 15,
        'description': 'Professional 8-piece kitchen knife set',
        'stock': 8,
    },
    {
        'name': 'Bed Sheets',
        'slug': 'bed-sheets',
        'category': home,
        'price': 1999,
        'discount_percent': 25,
        'description': 'Soft and comfortable cotton bed sheets',
        'stock': 25,
    },
]

# Create products
for p in products_data:
    stock = p.pop('stock')
    product = Product.objects.create(**p, is_active=True)
    Inventory.objects.create(product=product, stock=stock)

print(f"✅ Created {len(products_data)} sample products!")
