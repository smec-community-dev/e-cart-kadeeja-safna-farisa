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
    total_users = User.objects.count()
    total_sellers = Seller.objects.count()
    total_products = Product.objects.count()
    pending_orders = Orders.objects.filter(order_status="Pending").count()
    context = {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "total_products": total_products,
        "pending_orders": pending_orders,
    }

    return render(request,"core/admin_dashboard.html",context)

def manage_sellers(request):
    search_query = request.GET.get('q','')
    selected_status = request.GET.get('status','all')
    sellers = Seller.objects.all()
    s_address = Address.objects.all()
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

    paginator = Paginator(sellers,3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
            'page_obj': page_obj,
            'search_query': search_query,
            'selected_status': selected_status,
            's_address': s_address,
    }
    return render(request,'core/manage_sellers.html',context)

def approve_seller(request, id):
    user = get_object_or_404(User, id=id)
    seller = get_object_or_404(Seller, seller=user)  
    seller.verified = True
    seller.save()
    return redirect('manage_sellers')

def reject_seller(request, id):
    user = get_object_or_404(User, id=id)
    seller = get_object_or_404(Seller, seller=user)  
    seller.verified = False
    seller.save()
    return redirect('manage_sellers')

def manage_users(request):
    search_query = request.GET.get("search", "")
    if search_query:
        users_list = User.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    else:
        users_list = User.objects.all()

    paginator = Paginator(users_list, 5)  # 5 users per page
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)

    context = {
        'users': users_page,
        'search': search_query,
    }
    return render(request,'core/manage_users.html',context)

def toggle_user_status(user_id):
    user = get_object_or_404(User,id=user_id)
    user.status = not user.status
    user.save()

    return redirect("manage_users") 

def buyer_order_details(request,id):
    buyer = get_object_or_404(User,id=id,is_buyer=True)
    orders = Orders.objects.filter(user=buyer).order_by('-order_date')
    addresses = Address.objects.filter(user=buyer).order_by('-id')  
    orders = orders.prefetch_related('orderitem_set__Product')

    context = {
       'buyer' : buyer,
       'addresses': addresses,
       'orders' : orders,
    }
    return render(request,'core/buyer_order_details.html',context)

def order_in_details(request,id):
    order_items = get_object_or_404(OrderItem,id=id)
    return render(request,'core/order_in_details.html',order_items)

def manage_products(request):
    products = Product.objects.all()
    return render(request,'core/manage_products.html',{'products':products})

def manage_orders(request):
    return render(request,'core/manage_orders.html')

def manage_categories(request):
    return render(request,'core/manage_categories.html')

def manage_payments(request):
    return render(request,'core/manage_payments.html')