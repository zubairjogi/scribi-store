# File: store/views.py
# shop/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from decimal import Decimal
from .forms import SignupForm, ShippingForm
from .models import Profile, Category, Product, Cart, CartItem, Order, OrderItem
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.conf import settings


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        sender_email = request.POST.get('email')
        message = request.POST.get('message')

        full_message = f"Message from {name} ({sender_email}):\n\n{message}"

        try:
            send_mail(
                subject='New Contact Form Message',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully.")
        except BadHeaderError:
            messages.error(request, "Invalid header found.")
        except Exception as e:
            messages.error(request, f"Error sending message: {e}")

        return redirect('store:contact')

    return render(request, 'store/contact.html')

def home(request):
    """
    Renders the homepage with categories and featured products.
    """
    categories = Category.objects.all()
    featured_products = Product.objects.filter(available=True)[:4]
    
    # Get cart count for authenticated users
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured': featured_products,
        'cart_count': cart_count,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    images = product.images.all()
    return render(request, 'store/product_detail.html', {
        'product': product,
        'images': images,
    })
def signup(request):
    """
    Handles user signup with custom SignupForm.
    Creates both User and Profile objects.
    """
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            try:
                # Create the user with first and last name
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                )
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()
                
                # Update profile
                profile = user.profile
                profile.phone_number = form.cleaned_data['phone_number']
                profile.address_line1 = form.cleaned_data['address_line1']
                profile.address_line2 = form.cleaned_data.get('address_line2', '')
                profile.city = form.cleaned_data['city']
                profile.postal_code = form.cleaned_data['postal_code']
                profile.country = form.cleaned_data['country']
                profile.save()
                
                messages.success(
                    request,
                    f"Account created for {user.username}! You can now log in."
                )
                return redirect('store:login')
                
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
    else:
        form = SignupForm()

    return render(request, 'store/signup.html', {'form': form})

def login_view(request):
    """
    Handles user login with Django's AuthenticationForm.
    On success, sets an info message and redirects to home.
    """
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.info(request, f"Welcome back, {user.username}!")
            return redirect('store:home')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    """
    Logs out the current user and redirects to home with a message.
    """
    if request.method == 'POST':
        username = request.user.username if request.user.is_authenticated else "User"
        auth_logout(request)
        messages.info(request, f"Goodbye {username}! You have been logged out.")
        return redirect('store:home')
    
    # If GET request, redirect to home
    return redirect('store:home')

@login_required
def add_to_cart(request, product_id):
    """
    Adds a product to the user's cart.
    """
    product = get_object_or_404(Product, id=product_id, available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Updated {product.name} quantity in cart!")
    else:
        messages.success(request, f"Added {product.name} to cart!")
    
    return redirect(request.META.get('HTTP_REFERER', reverse('store:home')))

@login_required
def remove_from_cart(request, product_id):
    """
    Removes a product from the user's cart.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        messages.success(request, f"Removed {product.name} from cart!")
    except CartItem.DoesNotExist:
        messages.error(request, "Item not found in cart!")
    
    return redirect('store:cart')

@login_required
def update_cart_item(request, product_id):
    """
    Updates the quantity of a product in the cart.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = get_object_or_404(Cart, user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            return redirect('store:remove_from_cart', product_id=product_id)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f"Updated {product.name} quantity!")
        except CartItem.DoesNotExist:
            messages.error(request, "Item not found in cart!")
    
    return redirect('store:cart')

@login_required
def cart(request):
    """
    Displays the user's cart contents and total price.
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
    except Cart.DoesNotExist:
        cart_items = []

    for item in cart_items:
        final_price = item.product.get_final_price()
        item.total_price = final_price * item.quantity

    subtotal = sum(item.total_price for item in cart_items)
    cart_count = sum(item.quantity for item in cart_items)

    # Delivery charge logic
    delivery_charge = 0 if subtotal >= 1000 else 100
    grand_total = subtotal + delivery_charge

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'cart_count': cart_count,
    })


def category_detail(request, slug):
    """
    Displays products in a specific category.
    """
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, available=True)
    
    # Get cart count for authenticated users
    cart_count = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
    
    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': products,
        'cart_count': cart_count,
    })

@login_required
def checkout(request):
    """
    Handles the checkout process.
    """
    # Ensure user has a profile
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related('product').all()
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty!")
        return redirect('store:cart')

    if not cart_items:
        messages.error(request, "Your cart is empty!")
        return redirect('store:cart')

    subtotal = sum(item.product.get_final_price() * item.quantity for item in cart_items)
    delivery_charge = 0 if subtotal >= 1000 else 100
    total = subtotal + delivery_charge


    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                complete_address=form.cleaned_data['complete_address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                country=form.cleaned_data['country'],
                delivery_charge=delivery_charge,
                total_price=total,
            )

            # --- SEND PROFESSIONAL CONFIRMATION EMAILS ---
            WHATSAPP_NUMBER = "+92 300 1234567"  # ✅ Replace with your real number

            subject_user = f"🧾 Order Confirmation – Order #{order.order_id}"

            message_user = (
                f"Hello {order.full_name},\n\n"
                f"Thank you for shopping with Stationery Store!\n\n"
                f"We’re excited to let you know that we’ve received your order.\n\n"
                f"🛒 Order Summary:\n"
                f"Total Amount: Rs {order.total_price:.2f}\n"
                f"Email: {order.email}\n"
                f"Phone: {order.phone_number}\n\n"
                f"📦 Shipping Address:\n"
                f"{order.complete_address}\n"
                f"{order.city} – {order.postal_code}\n"
                f"{order.country}\n\n"
                f"You will receive another email once your items are shipped.\n"
                f"If you have any questions, feel free to contact us:\n"
                f"📧 Email: {settings.DEFAULT_FROM_EMAIL}\n"
                f"📱 WhatsApp: {WHATSAPP_NUMBER}\n\n"
                f"Best regards,\n"
                f"Stationery Store Team\n"
                f"{request.get_host()}"
            )

            subject_admin = f"📥 New Order Received – #{order.order_id}"

            message_admin = (
                f"A new order has been placed!\n\n"
                f"Order ID: {order.order_id}\n"
                f"Customer: {order.full_name}\n"
                f"Email: {order.email}\n"
                f"Phone: {order.phone_number}\n"
                f"Total: Rs {order.total_price:.2f}\n\n"
                f"Shipping Address:\n"
                f"{order.complete_address}\n"
                f"{order.city} – {order.postal_code}\n"
                f"{order.country}\n\n"
                f"WhatsApp Customer for Confirmation: {WHATSAPP_NUMBER}"
            )

            send_mail(
                subject_user,
                message_user,
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
                fail_silently=False,
            )

            send_mail(
                subject_admin,
                message_admin,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            # --- END EMAIL CODE ---

            # Create order items
            for item in cart_items:
                product = item.product
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                    discount_price=product.get_final_price() if product.discount_percentage > 0 else None
                )


            # Clear cart
            cart_items.delete()

            messages.success(request, f"Order {order.order_id} placed successfully!")
            return redirect('store:order_confirmation', order_id=order.order_id)
    else:
        form = ShippingForm()

    # Calculate total price per item for display
    for item in cart_items:
        item.total_price = item.product.get_final_price() * item.quantity


    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    })

@login_required
def order_confirmation(request, order_id):
    """
    Displays order confirmation.
    """
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # Calculate subtotal
    subtotal = order.total_price - order.delivery_charge

    return render(request, 'store/order_confirmation.html', {
        'order': order,
        'subtotal': subtotal,
    })

@login_required
def order_history(request):
    """
    Displays user's order history.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {
        'orders': orders,
    })

def custom_404_view(request, exception):
    try:
        return render(request, 'store/404.html', status=404)
    except Exception as e:
        return HttpResponse(f"404 error handler failed: {e}", status=500)