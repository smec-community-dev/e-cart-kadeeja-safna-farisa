from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from CoreApp.models import *
# Create your views here.
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
    return render(request,'register.html')


def user_login(request):
    if request.method == 'POST':
        email=request.POST['email']
        password=request.POST['password']
        user=authenticate(email=email,password=password)
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "User not Found.please try again")
            return redirect('login')
    return render(request,'login.html')


