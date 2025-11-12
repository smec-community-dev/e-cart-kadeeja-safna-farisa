from django.db import models
from django.contrib.auth.models import AbstractUser



# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [('buyer', 'Buyer'),('seller', 'Seller'),('admin','Admin')]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    class Meta:
        db_table='user_reg'



class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'category'


class SubCategory(models.Model):
    sub_category_id = models.AutoField(primary_key=True)
    category = models.ForeignKey('Category',on_delete=models.CASCADE)
    sub_category_name=models.CharField(max_length=50)
    description= models.TextField(blank=True,null=True)
