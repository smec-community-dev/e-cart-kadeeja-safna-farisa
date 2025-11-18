from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path("", views.index, name="index"),
    path("user/register/",views.user_reg,name='register'),
    path("user/login/",views.user_login,name='login'),
    path('user/home/',views.home,name='home'),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="cart"),
    path("cart/remove/<int:cart_id>/", views.remove_cart, name="remove_cart"),
    path("logout/",views.user_logout,name="logout"),
    path('checkout/',views.checkout,name="checkout"),
]
