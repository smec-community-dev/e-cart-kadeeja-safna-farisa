# seed.py
from django.contrib.auth import get_user_model
from CoreApp.models import Category, SubCategory
from SellerApp.models import Seller, Product, ProductImage
from UserApp.models import Reviews, Cart, WishList, Orders, OrderItem, Payment
from django.utils.text import slugify
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image as PilImage
import random
import os

User = get_user_model()

print("Seeding started...")

# ---- USERS (USING create_user → PASSWORD HASHED!) ----
buyer = User.objects.create_user(
    username="buyer1",
    password="buyerpass",
    email="buyer1@example.com",
    is_buyer=True,
    contact="9876543210",
    address="Kochi, Kerala, India"
)

seller_user = User.objects.create_user(
    username="seller1",
    password="sellerpass",
    email="seller1@example.com",
    is_seller=True,
    contact="9123456780",
    address="Calicut, Kerala, India"
)

admin_user = User.objects.create_user(
    username="admin",
    password="adminpass",
    email="admin@example.com",
    is_admin=True,
    is_superuser=True,
    is_staff=True,
    contact="9000000000",
    address="Admin HQ, India"
)

# ---- SELLER PROFILE ----
seller, _ = Seller.objects.get_or_create(
    seller=seller_user,
    defaults={
        "shop_name": "Tech Store",
        "verified": True,
        "description": "Your trusted store for gadgets!"
    }
)

# ---- CATEGORY & SUBCATEGORY ----
electronics, _ = Category.objects.get_or_create(category_name="Electronics")
fashion, _ = Category.objects.get_or_create(category_name="Fashion")
SubCategory.objects.get_or_create(category=electronics, sub_category_name="Mobiles")
SubCategory.objects.get_or_create(category=electronics, sub_category_name="Laptops")
SubCategory.objects.get_or_create(category=fashion, sub_category_name="Shirts")

# ---- PRODUCT LIST ----
product_names = [
    "iPhone 14 Pro Max", "Samsung Galaxy S23", "Xiaomi Redmi Note 12",
    "OnePlus 11 5G", "Vivo V29 Pro", "Oppo Reno 10", "Dell Inspiron Laptop",
    "HP Pavilion Aero", "Lenovo IdeaPad Slim", "Acer Nitro 5", "Asus ROG Strix",
    "Cotton Casual Shirt", "Denim Jacket", "Formal White Shirt",
    "Men’s Hoodie", "Women’s Kurti", "Sports Running Shoes",
    "Bluetooth Earbuds", "Apple AirPods", "Noise Smartwatch"
]

products = []
for name in product_names:
    product, _ = Product.objects.get_or_create(
        seller=seller_user,
        product_name=name,
        defaults={
            "product_price": random.randint(500, 80000),
            "category": random.choice([electronics, fashion]),
            "description": f"{name} - High quality and best pricing.",
            "stock": random.randint(3, 50)
        }
    )
    products.append(product)

# ---- REVIEWS, CART, etc. (same as before) ----
for p in products[:5]:
    Reviews.objects.get_or_create(
        product=p, user=buyer,
        defaults={"rating": random.randint(3, 5), "comment": "Great product!"}
    )

Cart.objects.get_or_create(product=products[0], user=buyer, defaults={"quantity": 2})
WishList.objects.get_or_create(product=products[1], user=buyer)

order, _ = Orders.objects.get_or_create(
    user=buyer,
    defaults={"amount": 1999.99, "order_status": "Confirmed"}
)
OrderItem.objects.get_or_create(order=order, Product=products[2], defaults={"quantity": 1})
Payment.objects.get_or_create(
    order=order, user=buyer,
    defaults={"amount": 1999.99, "payment_mode": "upi", "status": "Success", "transaction_id": "TRX123456"}
)

# ---- IMAGE GENERATOR FUNCTION ----
def create_placeholder_image(name: str, size=(400, 400), color=None):
    if color is None:
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    img = PilImage.new('RGB', size, color)
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
    text = name.replace(' ', '\n')
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill=(255, 255, 255), font=font)
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    return ContentFile(buffer.getvalue(), name=f"{slugify(name)}.jpg")

# ---- ADD IMAGES ----
print("Adding product images ...")
for idx, product in enumerate(products):
    img_file = create_placeholder_image(product.product_name)
    ProductImage.objects.get_or_create(product=product, defaults={"image": img_file})
    if idx < 3:
        for extra in range(1, 3):
            extra_name = f"{product.product_name} (extra {extra})"
            extra_file = create_placeholder_image(extra_name)
            ProductImage.objects.create(product=product, image=extra_file)

print(f"Created {ProductImage.objects.count()} product image(s).")
print("Seeding completed successfully!")