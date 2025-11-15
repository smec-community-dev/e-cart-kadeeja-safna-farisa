from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/",views.user_reg,name='register'),
    path("login/",views.user_login,name='login'),
]
