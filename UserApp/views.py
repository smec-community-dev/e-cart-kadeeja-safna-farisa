from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.core.paginator import Paginator
from CoreApp.models import *
from SellerApp.models import *
from django.db.models import Q
from decorators.decorator import role_required
from .models import *
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    search_query = request.GET.get('q', '')

    if search_query:
        products = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        ).order_by('-product_id')
    else:
       products = Product.objects.all().order_by('-product_id')

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "user/index.html",{"page_obj": page_obj,"search_query": search_query,})


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
            is_buyer=True,
            is_seller=False,
            is_admin=False
        )
        messages.success(request,"registration successful")
        return redirect('login')
    return render(request,'user/register.html')


def user_login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

        if not user.is_buyer:
            messages.error(request, "Not a valid user.")
            return redirect('login')

        login(request, user)
        return redirect("home")
    users=User.objects.all()
    return render(request, 'user/login.html',{'data':users})

@role_required('buyer',login_url='/user/login/')
def home(request):
    search_query = request.GET.get('q', '')

    if search_query:
        products = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        ).order_by('-product_id')
    else:
        products = Product.objects.all().order_by('-product_id')

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "user/home.html", {"page_obj": page_obj,"search_query": search_query,})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    images = product.productimage_set.all()

    in_cart = False
    cart_quantity = 0
    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, product=product).first()
        if cart_item:
            in_cart = True
            cart_quantity = cart_item.quantity
    return render(request, "user/product_detail.html", {"product": product, "images": images,"in_cart":in_cart,"cart_quantity":cart_quantity})


@role_required('buyer',login_url='/user/login/')
def add_to_cart(request,slug):

    product=get_object_or_404(Product,slug=slug)
    cart_item,created = Cart.objects.get_or_create(product=product,user=request.user,  defaults={"quantity": 1})
    if not created:
        cart_item.quantity += 1
        cart_item.save()


    return redirect('cart')



@role_required('buyer',login_url='/user/login/')
def view_cart(request):
    cart_items=Cart.objects.filter(user=request.user)
    total = sum(item.product.product_price * item.quantity for item in cart_items)
    return render(request,'user/cart.html',{'cart_items':cart_items,"total":total})

@role_required('buyer',login_url='/user/login/')
def remove_cart(request, cart_id):
    item = get_object_or_404(Cart, cart_id=cart_id, user=request.user)
    item.delete()
    return redirect("cart")

@role_required('buyer',login_url='/user/login/')
def checkout(request):
    cart_items=Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart')
    total = sum(item.product.product_price * item.quantity for item in cart_items)
    if request.method =="POST":
        order= Orders.objects.create(
             user=request.user,
            amount=total,
            order_status="pending",
        )
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
        )
        messages.success(request, "Order placed successfully!")
        return redirect('view_orders')
    return render(request,"user/checkout.html",{'cart_item' : cart_items,"total": total})

@role_required('buyer',login_url='/user/login/')
def view_orders(request):
    order=Orders.objects.filter(user=request.user)
    if not order.exists():
         messages.error(request,"No orders found")
    return render(request, "user/order_history.html", {'order': order})

def user_logout(request):
    logout(request)
    return redirect('index')

def add_to_wishlist(request):

