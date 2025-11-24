from django.shortcuts import render,redirect,get_object_or_404
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
        # address=request.POST['address']
        password=request.POST['password']
        re_password=request.POST['re_password']
        # Seller specific fields
        shop_name = request.POST['shop_name']
        description = request.POST['description']
        if not all([user_name, email, contact, password, re_password,shop_name,description]):
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
            # address=address,
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
                verified=True
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

    subcategories = SubCategory.objects.all()

    if request.method == "POST":

        subcategory_id = request.POST.get('subcategory')

        if not subcategory_id:
            messages.error(request, "Please select a subcategory.")
            return redirect('add_product')

        subcat = SubCategory.objects.get(sub_category_id=subcategory_id)

        product = Product.objects.create(
            seller=request.user,
            product_name=request.POST.get('name'),
            product_price=request.POST.get('price'),
            description=request.POST.get('description'),
            stock=request.POST.get('stock'),
            sub_category=subcat
        )
        images = request.FILES.getlist("images")
        for img in images:
            ProductImage.objects.create(product=product, image=img)

        messages.success(request, "Product added successfully.")
        return redirect('add_product')

    return render(request, 'seller/add_product.html', {
        'subcategories': subcategories
    })
def manage_product(request):
    products = Product.objects.filter(seller=request.user).prefetch_related('productimage_set')
    return render(request, "seller/manage_product.html", {
        "products": products
    })

def delete_product(request, product_id):
    product = Product.objects.get(product_id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully")
    return redirect("manage_product")

def edit_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    subcategories = SubCategory.objects.all()

    if request.method == "POST":
        product.product_name = request.POST.get("product_name")
        product.description = request.POST.get("description")
        product.product_price = request.POST.get("product_price")
        product.stock = request.POST.get("stock")
        product.sub_category_id = request.POST.get("sub_category")
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect("manage_product")

    return render(request, "seller/edit_product.html", {
        "product": product,
        "subcategories": subcategories
    })
def manage_orders(request):
    return render(request, 'seller/manage_order.html')


