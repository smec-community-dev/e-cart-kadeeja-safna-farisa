from django.db import models
from django.conf import settings
from SellerApp.models import Product
# Create your models here.
class Reviews(models.Model):
    review_id=models.AutoField(primary_key=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='review_images/',null=True)
    rating=models.IntegerField()
    comment=models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='Reviews'

class Cart(models.Model):
    cart_id=models.AutoField(primary_key=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    quantity=models.IntegerField()
    added_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='Cart'

class WishList(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    added_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='Wishlist'

class Orders(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Returned', 'Returned'),
        ('Refunded', 'Refunded'),]

    order_id=models.AutoField(primary_key=True)
    address=models.ForeignKey('Address',on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    order_status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='Orders'

class OrderItem(models.Model):
    order=models.ForeignKey('Orders',on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity=models.IntegerField()

    class Meta:
        db_table='order_item'

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('cod', 'Cash on Delivery'),
    ]
    PAYMENT_STATUS = [
        ('Pending','pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
    ]
    payment_id=models.AutoField(primary_key=True)
    order=models.ForeignKey(Orders,on_delete=models.CASCADE)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode=models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_date=models.DateTimeField(auto_now_add=True)
    transaction_id=models.CharField(max_length=100,blank=True,null=True)
    status = models.CharField(max_length=20,choices=PAYMENT_STATUS, default='Pending')
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table='Payment'

class Address(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    address=models.TextField(null=False,blank=False)
    class Meta:
        db_table="user_address"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table="contact messages"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=[
        ('order_update', 'Order Update'),
        ('promotion', 'Promotion'),
        ('system', 'System Notification'),
        ('welcome', 'Welcome Message')
    ])
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notifications'
        ordering = ['-created_at']

