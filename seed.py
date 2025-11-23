# seed.py
import os
import django
import random
from io import BytesIO
from django.utils.text import slugify
from django.core.files.base import ContentFile
from PIL import Image as PilImage
from PIL import ImageDraw


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Ecart.settings")
django.setup()

from django.contrib.auth import get_user_model
from CoreApp.models import Category, SubCategory
from SellerApp.models import Seller, Product, ProductImage
from UserApp.models import Reviews, Cart, WishList, Orders, OrderItem, Payment, Address

User = get_user_model()

print("🌱 SEEDING STARTED...")

# USERS
buyer = User.objects.create_user(username="buyer1", password="buyerpass", email="buyer1@example.com",
                                 is_buyer=True, contact="9876543210")
seller_user = User.objects.create_user(username="seller1", password="sellerpass",
                                       email="seller1@example.com", is_seller=True)
User.objects.create_superuser(username="admin", password="adminpass", email="admin@example.com")

# ADDRESS
buyer_address = Address.objects.create(user=buyer, address="Kochi, Kerala, India")

# SELLER PROFILE
Seller.objects.get_or_create(seller=seller_user,
                             defaults={"shop_name": "Best Store", "verified": True, "description": "Great deals!"})

# CATEGORY + SUBCATEGORY
categories = [
    ("Electronics", ["Mobiles", "Laptops", "Televisions", "Smartwatches"]),
    ("Fashion", ["Shirts", "T-Shirts", "Jackets", "Kurti"]),
    ("Home & Kitchen", ["Cookware", "Home Decor", "Lighting"]),
    ("Beauty", ["Skincare", "Haircare", "Makeup"]),
    ("Sports", ["Cricket", "Football", "Gym Equipment"]),
    ("Books", ["Fiction", "Study Materials"]),
]

all_subs = []

for cat_name, subs in categories:
    cat, _ = Category.objects.get_or_create(category_name=cat_name)
    for s in subs:
        sub, _ = SubCategory.objects.get_or_create(category=cat, sub_category_name=s)
        all_subs.append(sub)

# PRODUCTS
product_names = [
    "iPhone 15", "Samsung S24", "OnePlus 12", "Google Pixel 9", "Xiaomi Redmi Note 13",
    "MacBook Air M2", "Dell Inspiron 15", "HP Pavilion x360", "ASUS ROG Strix Gaming Laptop",
    "Nike Air Max Shoes", "Adidas Ultraboost", "Puma Running Shoes",
    "Peter England Shirt", "Levi’s Denim Jacket", "Allen Solly T-Shirt",
    "Prestige Pressure Cooker", "Samsung Microwave Oven", "Philips Air Fryer", "Stainless Steel Water Bottle",
    "Nivea Face Cream", "Lakme Sunscreen", "Dove Shampoo",
    "SS Cricket Bat", "Cosco Football",
    "Harry Potter Novel", "Rich Dad Poor Dad"
]

products = []
for name in product_names:
    p = Product.objects.create(
        seller=seller_user,
        product_name=name,
        product_price=random.randint(500, 99999),
        stock=random.randint(5, 50),
        sub_category=random.choice(all_subs),
        description=f"Best quality {name}",
    )
    products.append(p)

# REVIEWS, CART & WISHLIST
for p in products[:3]:
    Reviews.objects.create(product=p, user=buyer, rating=5, comment="Excellent!")

Cart.objects.create(user=buyer, product=products[0], quantity=2)
WishList.objects.create(user=buyer, product=products[1])

# ORDER + ITEM + PAYMENT
order = Orders.objects.create(user=buyer, address=buyer_address, amount=49999, order_status="Confirmed")
OrderItem.objects.create(order=order, product=products[0], quantity=1)
Payment.objects.create(order=order, user=buyer, amount=49999, payment_mode="upi", status="Success",
                       transaction_id="PAY123")

# IMAGE GENERATOR
def create_image(name):
    img = PilImage.new("RGB", (500, 500), (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)))
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), name[:12], fill="white")
    buf = BytesIO()
    img.save(buf, "JPEG")
    return ContentFile(buf.getvalue(), f"{slugify(name)}.jpg")

print("🖼 Adding product images...")
for p in products:
    ProductImage.objects.create(product=p, image=create_image(p.product_name))

print("✔ SEEDING DONE SUCCESSFULLY!")
print("\nLOGIN CREDENTIALS:\nbuyer1 / buyerpass\nseller1 / sellerpass\nadmin / adminpass")
