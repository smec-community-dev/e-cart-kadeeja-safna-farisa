from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path("login", views.admin_login, name="login"),
    path("admin-cart",views.admin_dashboard,name='admin_dashboard'),
    path("register",views.user_reg,name='admin_reg'),
    path('admin_dashboard',views.admin_dashboard,name='admin_dashboard'),
    path('manage_users',views.manage_users,name='manage_users'),
    path('manage_sellers',views.manage_sellers,name='manage_sellers'),
    path('manage_orders',views.manage_orders,name='manage_orders'),
    path('manage_categories',views.manage_categories,name='manage_categories'),
    path('manage_products',views.manage_products,name='manage_products'),
    path('manage_payments',views.manage_payments,name='manage_payments'),
    path('approve_seller/<int:id>',views.approve_seller,name='approve_seller'),
    path('reject_seller/<int:id>',views.reject_seller,name='reject_seller'),
]