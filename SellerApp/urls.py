from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path("register/", views.seller_reg, name='seller_reg'),
    path("login/",views.seller_login,name='seller_login'),
    path("seller_dashboard/",views.seller_dashboard,name='seller_dashboard'),
    path("add_product/",views.add_product,name='add_product'),
    path("manage_product/",views.manage_product,name='manage_product'),
    path("delete_product/<int:product_id>/", views.delete_product, name="delete_product"),
    path("edit_product/<int:product_id>/", views.edit_product, name="edit_product"),
    path("manage_orders",views.manage_orders,name="manage_orders"),
    path("delete_image/<int:image_id>/", views.delete_image, name="delete_image"),


]