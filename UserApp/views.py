from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from CoreApp.models import *
from SellerApp.models import *
# Create your views here.

def home(request):
    return render(request, "user/index.html")


def user_reg(request):
    if request.method=="Post":
        user_name =request.POST['username']
        email=request.POST['email']
        role=request.POST['role']
        contact=request.POST['contact']
        address=request.POST['address']
        password=request.POST['password']
        re_password=request.POST['re_password']
        if not all([user_name, email, contact, address, password, re_password, role]):
            messages.error(request, "All fields are required.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Try logging in.")
            return redirect('register')
        if password != re_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        User.objects.create_user(
           username=user_name,
            email=email,
            password=password,
            contact=contact,
            address=address,
            role=role
        )
        return redirect('login')
    return render(request,'user/register.html')


def user_login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
        if user.role == "buyer":
            login(request, user)
            return redirect("home")
    return render(request,'login.html')


def view_product(request):
    product=Product.objects.all()

