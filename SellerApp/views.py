from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from SellerApp.models import *
from CoreApp.models import *
def seller_reg(request):
    user=User.objects.all()

    if request.method=="POST":
        user_name=request.POST['name']
        email=request.POST['email']
        contact=request.POST['contact']
        address=request.POST['address']
        password=request.POST['password']
        re_password=request.POST['re_password']
        # Seller specific fields
        shop_name = request.POST['shop_name']
        description = request.POST['description']
        if not all([user_name, email, contact, address, password, re_password,shop_name,description]):
            messages.error(request, "All fields are required.")
            return redirect('seller_reg')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Try logging in.")
            return redirect('seller_reg')
        if password != re_password:
            messages.error(request, "Passwords do not match.")
            return redirect('seller_reg')
        user=User.objects.create_user(
            username=user_name,
            email=email,
            contact=contact,
            address=address,
            password=password,
            is_buyer=False,
            is_seller=True,
            is_admin=False
        )

        # Create Seller table only for sellers
        if user.is_seller:
            Seller.objects.create(
                seller=user,
                shop_name=shop_name,
                description=description,
                # verified=True
            )

        messages.success(request, "Registration successful! Please login.")
        return redirect('seller_login')
    return render(request,'seller/register.html',{'data':user})


def seller_login(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(username=user_name, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('seller_login')

        # Check role
        if not user.is_seller:
            messages.error(request, "You are not registered as a seller.")
            return redirect('seller_login')

        # Check if seller profile exists
        try:
            seller = Seller.objects.get(seller=user)
        except Seller.DoesNotExist:
            messages.error(request, "Seller profile not found.")
            return redirect('seller_login')

        # Check if seller is verified
        if not seller.verified:
            messages.error(request, "Your seller account is not verified yet.")
            return redirect('seller_login')

        # Final: Login seller
        login(request, user)
        return redirect('seller_dashboard')

    return render(request, 'seller/seller_login.html')
def seller_dashboard(request):
    return render(request,'seller/seller_dashboard.html')
def add_product(request):
    if request.method=="POST":
        Add_Product=Product()
        Add_Product.product_name=request.POST.get('name')
        Add_Product.product_price=request.POST.get('price')
        Add_Product.description=request.POST.get('description')
        Add_Product.stock=request.POST.get('stock')
        Add_Product.save()
        return redirect('add_product')
    return render(request,'seller/add_product.html')
def delete_product(request,id):
    Add_Product=Product.objects.get(product_id=id)
    Add_Product.delete()
    return redirect('manage_product')
def update_product(request,id):
    Add_Product=Product.objects.get(product_id=id)
    if request.method=="POST":
        Add_Product.product_name=request.POST.get('name')
        Add_Product.product_price=request.POST.get('price')
        Add_Product.description=request.POST.get('description')
        Add_Product.stock=request.POST.get('stock')
        Add_Product.save()
        return redirect('add_product')
    return render(request,'add_product.html')





