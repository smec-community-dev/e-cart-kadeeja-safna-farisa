from django.db import models
from django.conf import settings
from CoreApp.models import Category
from django.utils.text import slugify
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
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Create slug only if not exists
            base_slug = slugify(self.product_name)
            slug = base_slug
            counter = 1
            # Ensure unique slug
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        db_table = "product"

class ProductImage(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    class Meta:
        db_table="product_Image"

