from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from CoreApp.models import *
from SellerApp.models import *
from django.db.models import Q
from decorators.decorator import role_required
from .models import *
from .notifications import send_notification
import razorpay
import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Notification

# Create your views here.

def index(request):
    search_query = request.GET.get('q', '')

    if search_query:
        products = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        ).order_by('-product_id')
    else:
       products = Product.objects.all().order_by('-product_id')[:4]

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        wishlist_count = WishList.objects.filter(user=request.user).count()
    categories = Category.objects.all()
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'cart_items': cart_count,  # ← for navbar badge
        'wishlist_count': wishlist_count,
        'categories': categories,
    }
    return render(request, "user/index.html", context)


def user_reg(request):
    if request.method == "POST":
        user_name = request.POST['username']
        email = request.POST['email']
        contact = request.POST['contact']
        password = request.POST['password']
        re_password = request.POST['re_password']

        if not all([user_name, email, contact, password, re_password]):
            messages.error(request, "All fields are required.")
            return redirect('userapp:register')  # Use namespaced URL

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered. Try logging in.")
            return redirect('userapp:register')  # Use namespaced URL

        if password != re_password:
            messages.error(request, "Passwords do not match.")
            return redirect('userapp:register')  # Use namespaced URL

        # Create user - the signal will automatically handle post-registration actions
        user=User.objects.create_user(
            username=user_name,
            email=email,
            password=password,
            contact=contact,
            status=True,
            is_buyer=True,
            is_seller=False,
            is_admin=False
        )
        send_notification(user, "Welcome to our platform!", "welcome")
        messages.success(request, "Registration successful! Please login.")
        return redirect('userapp:login')  # Use namespaced URL

    return render(request, 'user/register.html')


def redirect_by_user_type(request):
    if not request.user.is_authenticated:
        return redirect('userapp:login')

    # Check if Google login placed redirect session
    redirect_to = request.session.pop("redirect_to", None)
    if redirect_to:
        return redirect(redirect_to)

    # Normal login redirection
    if request.user.is_buyer:
        return redirect('userapp:index')
    elif request.user.is_seller:
        return redirect('sellerapp:index')
    elif request.user.is_admin:
        return redirect('adminapp:index')

    return redirect('userapp:index')




def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect('userapp:login')  # Use namespaced URL

        if not user.status:
            messages.error(request, "This account is restricted.")
            return redirect('userapp:login')  # Use namespaced URL

        # Login the user - this will trigger the user_logged_in signal
        login(request, user)
        send_notification(user, "You have logged in successfully!", "system")

        # Check for offline notifications
        offline_notifications = Notification.objects.filter(user=user, is_read=False)

        if offline_notifications.exists():
            messages.info(request, f"You have {offline_notifications.count()} new notifications")

        # Use the redirect function to send users to appropriate pages
        return redirect_by_user_type(request)

    return render(request, 'user/login.html')


@role_required('buyer',login_url='/user/login/')
def home(request):
    search_query = request.GET.get('q', '')

    if search_query:
        products = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        ).order_by('-product_id')
    else:
        products = Product.objects.all().order_by('-product_id')[:5]

    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "user/home.html", {"page_obj": page_obj,"search_query": search_query,})


def product_detail(request, slug):
    try:
        product = get_object_or_404(Product, slug=slug)
        images = product.productimage_set.all()
        reviews = Reviews.objects.filter(product=product).order_by('-created_at')

        can_review = False
        if request.user.is_authenticated:
            has_delivered = OrderItem.objects.filter(
                order__user=request.user,
                order__order_status='Delivered',
                product=product
            ).exists()

            already_reviewed = Reviews.objects.filter(product=product, user=request.user).exists()

            can_review = has_delivered and not already_reviewed
        if request.method == "POST" and 'submit_review' in request.POST:
            if not can_review:
                messages.error(request, "You can only review products you've received.")
            else:
                rating = request.POST.get('rating')
                comment = request.POST.get('comment')
                image = request.FILES.get('image')

                if not rating:
                    messages.error(request, "Please select a rating.")
                else:
                    Reviews.objects.create(
                        product=product,
                        user=request.user,
                        rating=int(rating),
                        comment=comment or None,
                        image=image
                    )
                    messages.success(request, "Thank you! Your review has been added.")
                    return redirect('userapp:product_detail', slug=slug)

        in_wishlist = False
        if request.user.is_authenticated:
            in_wishlist = WishList.objects.filter(user=request.user, product=product).exists()

        cart_item = None
        if request.user.is_authenticated:
            cart_item = Cart.objects.filter(user=request.user, product=product)
        return render(request, "user/product_detail.html", {"product": product, "images": images,'in_wishlist':in_wishlist, "cart_item": cart_item,'reviews': reviews,
        'can_review': can_review,})
    except Product.DoesNotExist:
        messages.error(request,"product not available")
        return redirect('userapp:home')

@role_required('buyer',login_url='/user/login/')
def add_to_cart(request,slug):
    if request.method!="POST":
        return redirect('userapp:product_detail',slug=slug)

    product=get_object_or_404(Product,slug=slug)
    if product.stock < 1:
        messages.error(request, "This product is out of stock.")
        return redirect('userapp:product_detail', slug=slug)
    try:
        quantity = int(request.POST.get('quantity'))
    except:
        quantity = 1

    if quantity > product.stock:
        messages.warning(request, f"Only {product.stock} items available in stock.")
        return redirect('userapp:product_detail', slug=slug)

    cart_item,created = Cart.objects.get_or_create(product=product,user=request.user,  defaults={"quantity":quantity  })
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('userapp:cart')

@role_required('buyer',login_url='/user/login/')
def update_cart(request,cart_id):
    cart_item = get_object_or_404(Cart, cart_id=cart_id)
    if request.method == "POST":
        new_qty = int(request.POST.get('quantity'))
        if new_qty > cart_item.product.stock:
            messages.error(request, "Quantity exceeds available stock!")
        else:
            cart_item.quantity = new_qty
            cart_item.save()
            messages.success(request, "Quantity updated successfully")
    return redirect("userapp:cart")

@role_required('buyer',login_url='/user/login/')
def view_cart(request):
    cart_items=Cart.objects.filter(user=request.user)
    total = sum(item.product.product_price * item.quantity for item in cart_items)
    return render(request,'user/cart.html',{'cart_items':cart_items,"total":total})

@role_required('buyer',login_url='/user/login/')
def remove_cart(request, cart_id):
    item = get_object_or_404(Cart, cart_id=cart_id, user=request.user)
    item.delete()
    return redirect("userapp:cart")

@role_required('buyer', login_url='/user/login/')
def checkout(request):
    # Razorpay client (safe to keep here)
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    if request.GET.get('clear'):
        return redirect('userapp:checkout')

    buynow = request.GET.get('buy_now')
    product_id = request.GET.get('product_id')
    quantity = int(request.GET.get('quantity', 1))

    cart_items = None
    buy_now_product = None
    total = 0

    # ---------------- BUY NOW FLOW ----------------
    if buynow and product_id:
        buy_now_product = get_object_or_404(Product, product_id=product_id)

        if buy_now_product.stock < quantity:
            messages.error(request, "Insufficient stock!")
            return redirect('userapp:product_detail', buy_now_product.slug)

        total = buy_now_product.product_price * quantity

    # ---------------- CART FLOW ----------------
    else:
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.info(request, "Your cart is empty!")
            return redirect('userapp:cart')

        total = sum(item.product.product_price * item.quantity for item in cart_items)

    addresses = Address.objects.filter(user=request.user)

    # ================= POST REQUEST =================
    if request.method == "POST":
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')

        if not address_id:
            messages.error(request, "Please select an address.")
            return redirect('userapp:checkout')

        address = get_object_or_404(Address, id=address_id, user=request.user)

        # -------- Create Order (COMMON FOR BOTH) --------
        order = Orders.objects.create(
            user=request.user,
            address=address,
            amount=total,
            order_status='Pending'
        )

        # -------- Save Order Items + Reduce Stock --------
        if buynow:
            OrderItem.objects.create(
                order=order,
                product=buy_now_product,
                quantity=quantity
            )
            buy_now_product.stock -= quantity
            buy_now_product.save()
        else:
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )
                item.product.stock -= item.quantity
                item.product.save()
            cart_items.delete()

        # ================= COD FLOW =================
        if payment_method == 'cod':
            Payment.objects.create(
                order=order,
                user=request.user,
                amount=total,
                payment_mode='cod',
                status='Pending'
            )

            send_notification(request.user, "Order placed successfully!", "order_update")
           
            return redirect('userapp:orders')

        # ================= ONLINE PAYMENT FLOW =================
        razorpay_order = client.order.create({
            "amount": int(total * 100),  # in paise
            "currency": "INR",
            "payment_capture": 1
        })

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=total,
            payment_mode='upi',
            razorpay_order_id=razorpay_order['id'],
            status='Pending'
        )

        # Redirect to Razorpay popup page
        return render(request, 'user/razorpay_checkout.html', {
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order': order,
            'payment': payment,
            'amount': int(total * 100),
        })

    # ================= GET REQUEST =================
    return render(request, 'user/checkout.html', {
        'cart_items': cart_items,
        'buy_now_product': buy_now_product,
        'buy_now_quantity': quantity,
        'total': total,
        'addresses': addresses,
        'is_buy_now': bool(buynow),
    })

@csrf_exempt
def razorpay_verify(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))

        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_signature = data.get("razorpay_signature")

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature
            })

            payment = get_object_or_404(
                Payment, razorpay_order_id=razorpay_order_id
            )

            payment.transaction_id = razorpay_payment_id
            payment.status = "Success"
            payment.save()

            order = payment.order
            order.order_status = "Confirmed"
            order.save()

            return JsonResponse({"status": "success"})

        except Exception:
            return JsonResponse({"status": "failed"}, status=400)







@role_required('buyer',login_url='/user/login/')
def view_orders(request):
    orders=Orders.objects.filter(user=request.user)
    for order in orders:
        for item in order.orderitem_set.all():
            item.has_reviewed = Reviews.objects.filter(
                product=item.product,
                user=request.user
            ).exists()
    if not orders.exists():
         messages.error(request,"No orders found")
    return render(request, "user/order_history.html", {'orders': orders})

@role_required('buyer',login_url='/user/login/')
def wishlist(request,slug):
    product=get_object_or_404(Product,slug=slug)
    wishlist,created=WishList.objects.get_or_create(user=request.user,product=product)
    if not created:
        wishlist.delete()
        messages.success(request,f"{product.product_name} removed from wishlist")
    else:
        messages.success(request,f"{product.product_name} added to wishlist")
    return redirect('userapp:product_detail',slug=slug)

@role_required('buyer',login_url='/user/login/')
def view_wishlist(request):
    wishlist=WishList.objects.filter(user=request.user)
    return render(request,"user/view_wishlist.html",{'wishlist':wishlist})

@role_required('buyer',login_url='/user/login/')
def profile(request):
    return render(request,"user/profile.html")

@role_required('buyer',login_url='/user/login/')
def dashboard(request):
    # Get counts
    orders_count = Orders.objects.filter(user=request.user).count()
    wishlist_count = WishList.objects.filter(user=request.user).count()
    addresses_count = Address.objects.filter(user=request.user).count()

    # Get recent 5 orders (latest first)
    recent_orders = Orders.objects.filter(user=request.user).order_by('-order_date')[:5]

    context = {
        'orders_count': orders_count,
        'wishlist_count': wishlist_count,
        'addresses_count': addresses_count,
        'recent_orders': recent_orders,
    }
    return render(request, 'user/dashboard.html', context)

@role_required('buyer',login_url='/user/login/')
def address(request):
    address_list=Address.objects.filter(user=request.user)
    return render(request,"user/address.html",{'address':address_list})

@role_required('buyer',login_url='/user/login/')
def add_address(request):
    if request.method == "POST":
        address_text = request.POST.get("address")
        if address_text:
            Address.objects.create(user=request.user, address=address_text)
            messages.success(request, "New address added!")
        return redirect('userapp:address')
    return redirect('userapp:address')

@role_required('buyer',login_url='/user/login/')
def edit_address(request, address_id):
    address=Address.objects.filter(user=request.user)
    addr = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == "POST":
        address_text = request.POST.get("address")
        if address_text:
            addr.address = address_text
            addr.save()
            messages.success(request, "Address updated!")
        return redirect('userapp:address')
    return render(request, "user/address.html", {"edit_address": addr,"address": address})


@role_required('buyer',login_url='/user/login/')
def delete_address(request, address_id):
    addr = get_object_or_404(Address, id=address_id, user=request.user)
    addr.delete()
    messages.success(request, "Address deleted successfully!")
    return redirect("userapp:address")

@role_required('buyer',login_url='/user/login/')
def password_change(request):

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
        elif new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
        elif len(new_password1) < 8:
            messages.error(request, "New password must be at least 8 characters.")
        else:
            request.user.set_password(new_password1)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keeps user logged in
            messages.success(request, "Password changed successfully!")
            return redirect('userapp:dashboard')
    return render(request,"user/manage_passwords.html")

@role_required('buyer',login_url='/user/login/')
def edit_profile(request):
    user=request.user
    if request.method == "POST":
        user.username=request.POST['username']
        user.email=request.POST['email']
        user.contact=request.POST['contact']
        user.save()
        messages.success(request,"profile updated successfully")
    return render(request,"user/edit_profile.html")


def user_logout(request):
    logout(request)
    return redirect('userapp:index')

def about(request):
    return render(request,'user/about.html')

def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            subject=request.POST['subject'],
            message=request.POST['message']
        )
        messages.success(request, "Thank you! Your message has been sent. We'll reply soon.")
        return redirect('userapp:contact')
    return render(request, 'user/contact.html')

def shop(request, category_id=None, subcategory_id=None):
    categories = Category.objects.all().prefetch_related('subcategory_set')

    selected_category = None
    selected_subcategory = None

    products = Product.objects.filter(stock__gt=0).select_related('sub_category__category')


    if category_id:
        selected_category = get_object_or_404(Category, category_id=category_id)
        products = products.filter(sub_category__category=selected_category)


    if subcategory_id:
        selected_subcategory = get_object_or_404(SubCategory, sub_category_id=subcategory_id)
        products = products.filter(sub_category=selected_subcategory)
        selected_category = selected_subcategory.category  # for highlighting

    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query)
        )


    price_min = request.GET.get('price__gte')
    price_max = request.GET.get('price__lte')
    if price_min:
        products = products.filter(product_price__gte=price_min)
    if price_max:
        products = products.filter(product_price__lte=price_max)


    products = products.order_by('-product_id')
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'selected_subcategory': selected_subcategory,
        'query': query,
    }
    return render(request, 'user/shop.html', context)

@role_required('buyer',login_url='/user/login/')
def fetch_notifications(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    data = [
        {"id": n.id, "message": n.message, "type": n.notification_type, "created": n.created_at.strftime("%d %b %Y %I:%M %p")}
        for n in notifications
    ]
    return JsonResponse({"notifications": data, "count": len(data)})

@role_required('buyer',login_url='/user/login/')
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({"status": "success"})

