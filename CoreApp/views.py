from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from django.contrib import messages
from SellerApp.models import *
from UserApp.models import *
def admin_reg(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        role = request.POST['role']
        contact = request.POST['contact']
        address = request.POST['address']
        password = request.POST['password']
        re_password = request.POST['re_password']
        if not all([username, email, contact, address, password, re_password, role]):
            messages.error(request, "All fields are required.")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Try logging in.")
            return redirect('register')
        if password != re_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        User.objects.create_user(
           username=username,
            email=email,
            password=password,
            contact=contact,
            address=address,
            role=role
        )
        return redirect('login')
    return render(request,'register.html')
def seller_approval(request,id):
    obj = Seller.objects.get()    
    return render(request,'manage_sellers.html')
