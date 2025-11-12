from django.db import models
from django.conf import settings
from CoreApp.models import Category

# Create your models here.

class Seller(models.Model):
    seller = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100)
    verified = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        db_table='seller'

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    product_price = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    stock = models.IntegerField()

    class Meta:
        db_table = "product"

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    class Meta:
        db_table="product_Image"

