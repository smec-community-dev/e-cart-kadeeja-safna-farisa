from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from SellerApp.models import *
from UserApp.models import *
from CoreApp.models import *

def user_reg(request):
    if request.method=="POST":
        user_name =request.POST['username']
        email=request.POST['email']
        contact=request.POST['contact']
        address=request.POST['address']
        password=request.POST['password']
        re_password=request.POST['re_password']
        if not all([user_name, email, contact, address, password, re_password]):
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
            is_buyer = False,
            is_seller = False,
            is_admin = True,
        )
        return redirect('login')
    return render(request,'core/register.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
        if user.is_admin:
            login(request, user)
            return redirect("admin_dashboard")
    return render(request,'core/login.html')

def admin_dashboard(request):
    return render(request,"core/admin_dashboard.html")

def manage_sellers(request):
    search_query = request.GET.get('q','')
    selected_status = request.GET.get('status','all')
    sellers = Seller.objects.all()

    if search_query :
        sellers = sellers.filter(
            Q(shop_name__icontains = search_query) |
            Q(seller__username__icontains = search_query)
        )

    if selected_status and selected_status != 'all':
            if selected_status == 'verified':
                sellers = sellers.filter(verified=True)
            elif selected_status == 'rejected':
                sellers = sellers.filter(verified=False)

    paginator = Paginator(sellers,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'selected_status': selected_status,
    }
    return render(request,'core/manage_sellers.html',context)

def approve_seller(request, id):
    user = get_object_or_404(User, id=id)
    seller = get_object_or_404(Seller, seller=user)  
    seller.verified = True
    seller.save()

    messages.success(request, "Seller approved successfully!")
    return redirect('manage_sellers')


def reject_seller(request, id):
    user = get_object_or_404(User, id=id)
    seller = get_object_or_404(Seller, seller=user)  
    seller.verified = False
    seller.save()

    messages.error(request, f"{seller.seller.username} rejected")
    return redirect('manage_sellers')

def manage_users(request):
    users = User.objects.all()
    return render(request,'core/manage_users.html',{'users':users})

def block_user(request):
            
    return redirect('core/manage_user.html')

def manage_products(request):
    products = Product.objects.all()
    return render(request,'core/manage_products.html',{'products':products})

def manage_orders(request):
    return render(request,'core/manage_orders.html')

def manage_categories(request):
    return render(request,'core/manage_categories.html')

def manage_payments(request):
    return render(request,'core/manage_payments.html')