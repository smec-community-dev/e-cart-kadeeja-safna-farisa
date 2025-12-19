from django.contrib import admin
from django.urls import path
from .import views

app_name = 'UserApp'

urlpatterns = [
    path("", views.index, name="index"),
    path('shop/', views.shop, name='shop'),
    path('shop/category/<int:category_id>/', views.shop, name='shop_by_category'),
    path('shop/subcategory/<int:subcategory_id>/', views.shop, name='shop_by_subcategory'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('all-products/', views.index, name='all_products'),
    path("user/register/",views.user_reg,name='register'),
    path("user/login/",views.user_login,name='login'),
    path('redirect/', views.redirect_by_user_type, name='redirect_by_type'),
    path('user/home/',views.home,name='home'),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="cart"),
    path("update_cart/<int:cart_id>",views.update_cart,name="update_cart"),
    path("cart/remove/<int:cart_id>/", views.remove_cart, name="remove_cart"),
    path("logout/",views.user_logout,name="logout"),
    path('checkout/',views.checkout,name="checkout"),
    path('wishlist/<slug:slug>',views.wishlist,name="wishlist"),
    path("view_wishlist/",views.view_wishlist,name="view_wishlist"),
    path('profile/',views.profile,name="profile"),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('address/', views.address, name="address"),
    path('address/add/', views.add_address, name="add_address"),
    path('address/edit/<int:address_id>/', views.edit_address, name="edit_address"),
    path('address/delete/<int:address_id>/', views.delete_address, name="delete_address"),
    path("edit_profile/",views.edit_profile,name="edit_profile"),
    path('manage_passwords/',views.password_change,name="password_change"),
    path("orders/",views.view_orders,name="orders"),
    path("notifications/fetch/", views.fetch_notifications, name="fetch_notifications"),
    path("notifications/mark-read/", views.mark_notifications_read, name="mark_notifications_read"),
    path('razorpay/verify/', views.razorpay_verify, name='razorpay_verify'),


]
