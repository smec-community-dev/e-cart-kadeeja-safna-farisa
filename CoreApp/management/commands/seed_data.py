import os
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings

User = get_user_model()

# Import all your models
from CoreApp.models import *
from SellerApp.models import*
from UserApp.models import * 

class Command(BaseCommand):
    help = 'Seed database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Create Superuser (optional)
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin/admin123'))

        # 2. Create Buyers
        buyers = []
        for i in range(1, 6):
            username = f'buyer{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'buyer{i}@example.com',
                    password='buyer123',
                    is_buyer=True,
                    contact=f'98765432{i}',
                    address=f'Address of buyer {i}, India'
                )
                buyers.append(user)
                self.stdout.write(f"Created buyer: {username}")

        # 3. Create Sellers (verified=False)
        sellers = []
        for i in range(1, 4):
            username = f'seller{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'seller{i}@example.com',
                    password='seller123',
                    is_seller=True,
                    is_buyer=False,
                    contact=f'91234567{i}',
                    address=f'Shop address of seller {i}'
                )
                seller = Seller.objects.create(
                    seller=user,
                    shop_name=f"Shop of Seller {i}",
                    verified=False,  # As requested
                    description=f"Amazing shop by seller {i} selling quality products."
                )
                sellers.append(seller)
                self.stdout.write(f"Created seller: {username} (verified=False)")

        # 4. Categories & Subcategories
        categories_data = [
            ("Electronics", "Gadgets and devices", ["Mobiles", "Laptops", "Accessories"]),
            ("Fashion", "Clothing and accessories", ["Men", "Women", "Kids"]),
            ("Home & Kitchen", "Everything for your home", ["Furniture", "Appliances", "Decor"]),
        ]

        categories = []
        for cat_name, desc, subcats in categories_data:
            cat, created = Category.objects.get_or_create(
                category_name=cat_name,
                defaults={'description': desc}
            )
            if created:
                self.stdout.write(f"Created category: {cat_name}")
            categories.append(cat)

            for sub_name in subcats:
                SubCategory.objects.get_or_create(
                    category=cat,
                    sub_category_name=sub_name,
                    defaults={'description': f"Subcategory for {sub_name}"}
                )

        # 5. Products + Images
        product_data = [
            ("iPhone 15 Pro", 99900, "Latest Apple iPhone with A17 Pro", 10, categories[0]),
            ("Samsung Galaxy S24", 79900, "Flagship Android phone", 15, categories[0]),
            ("MacBook Air M2", 109900, "Light and powerful laptop", 5, categories[0]),
            ("Cotton T-Shirt Men", 799, "Comfortable casual t-shirt", 50, categories[1]),
            ("Women Kurti Set", 1499, "Ethnic wear with dupatta", 30, categories[1]),
            ("Wooden Dining Table", 24999, "6-seater solid wood table", 8, categories[2]),
        ]

        placeholder_images = [
            "https://loremflickr.com/800/800/iphone,smartphone",
            "https://loremflickr.com/800/800/samsung,phone",
            "https://loremflickr.com/800/800/macbook,laptop",
            "https://loremflickr.com/800/800/tshirt,fashion",
            "https://loremflickr.com/800/800/kurti,indian",
            "https://loremflickr.com/800/800/dining,table,furniture",
        ]

        products = []
        for i, (name, price, desc, stock, category) in enumerate(product_data):
            seller_user = sellers[i % len(sellers)].seller

            product = Product.objects.create(
                seller=seller_user,
                product_name=name,
                product_price=price,
                category=category,
                description=desc,
                stock=stock,
            )
            products.append(product)
            self.stdout.write(f"Created product: {name}")

            # Download and attach image
            image_url = placeholder_images[i]
            response = requests.get(image_url)
            if response.status_code == 200:
                image_name = f"product_{product.product_id}_{i}.jpg"
                product_image = ProductImage(product=product)
                product_image.image.save(image_name, ContentFile(response.content), save=True)
                self.stdout.write(f"   Added image for {name}")

        # 6. Reviews
        for product in products[:4]:
            for buyer in buyers[:3]:
                Reviews.objects.create(
                    product=product,
                    user=buyer,
                    rating=4 if buyer.username != 'buyer3' else 5,
                    comment=f"Great product! Loved it." if buyer.username != 'buyer2' else "Good value for money."
                )

        # 7. Cart & Wishlist
        for buyer in buyers[:3]:
            Cart.objects.create(product=products[0], user=buyer, quantity=1)
            Cart.objects.create(product=products[1], user=buyer, quantity=2)
            WishList.objects.create(user=buyer, product=products[2])

        # 8. Orders + OrderItems + Payment
        for buyer in buyers[:2]:
            order = Orders.objects.create(
                user=buyer,
                amount=99900 + 79900,  # iPhone + Samsung
                order_status='Confirmed'
            )

            OrderItem.objects.create(order=order, Product=products[0], quantity=1)
            OrderItem.objects.create(order=order, Product=products[1], quantity=1)

            Payment.objects.create(
                order=order,
                user=buyer,
                amount=order.amount,
                payment_mode='upi',
                transaction_id=f"TXN{order.order_id}12345",
                status='Success'
            )

            # One COD pending order
            order2 = Orders.objects.create(
                user=buyer,
                amount=1499,
                order_status='Pending'
            )
            OrderItem.objects.create(order=order2, Product=products[4], quantity=2)
            Payment.objects.create(
                order=order2,
                user=buyer,
                amount=order2.amount,
                payment_mode='cod',
                status='Pending'
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded all dummy data!"))
