from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path("register/", views.seller_reg, name='seller_reg'),
    path("login/",views.seller_login,name='seller_login'),
    path("seller_dashboard/",views.seller_dashboard,name='seller_dashboard'),
    path("add_product/",views.add_product,name='add_product')
]