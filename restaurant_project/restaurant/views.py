from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .models import Product, Cart, Order, OrderItem
from django.contrib.auth.models import User
from django.utils.timezone import localdate
from datetime import date
import uuid
from .forms import ProductForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm
import random
import string
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()  # This gets your custom User model (restaurant.User)


def generate_order_id():
    # Generate a random 8-character alphanumeric order ID
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


# View for viewing orders of a specific user (for the manager)
def view_user_orders(request):
    users = User.objects.all()
    selected_user_orders = None
    if request.method == "GET" and 'user' in request.GET:
        user_id = request.GET.get('user')
        selected_user_orders = Order.objects.filter(user__id=user_id)

    return render(request, 'manager_dashboard.html', {
        'users': users,
        'selected_user_orders': selected_user_orders
    })


# View to add products (for the manager)
def add_product_form(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = ProductForm()

    return render(request, 'form.html', {'form': form})


# API to get cart data for the user
def get_cart_data(request):
    cart_items = Cart.objects.filter(user=request.user)

    cart_data = []
    for item in cart_items:
        cart_data.append({
            'id': item.id,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'unit_price': float(item.product.discounted_price()),
            'total_price': float(item.total_price()),
            'instruction': item.instruction,  # Include instruction if needed
        })

    return JsonResponse({'items': cart_data})


# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('manager_dashboard' if user.user_type == 'manager' else 'customer_dashboard')
            else:
                return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


# Register view
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = True
            user.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


# Manager dashboard
@login_required
def manager_dashboard(request):
    orders = Order.objects.all()
    latest_order_date = Order.objects.latest("date_ordered").date_ordered if Order.objects.exists() else None

    if request.method == 'POST' and 'add_product' in request.POST:
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = ProductForm()
    return render(request, 'manager_dashboard.html', {'form': form, 'orders': orders})


# Customer dashboard
@login_required
def customer_dashboard(request):
    products = Product.objects.all()
    return render(request, "customer_dashboard.html", {"products": products})


# Add to cart
@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)

        # Check if the product is already in the cart
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        messages.success(request, f"{product.name} added to cart successfully!")
        return redirect("view_cart")


# View cart
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    current_date = date.today().isoformat()
    customers = User.objects.filter(user_type='customer')

    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        instructions = {key.split('_')[1]: value for key, value in request.POST.items() if key.startswith('instruction_')}
        user = request.user

        for item_id in selected_items:
            cart_item = get_object_or_404(Cart, id=item_id)

            # Avoid duplicate orders for the same day
            if OrderItem.objects.filter(order__user=user, product=cart_item.product, order__date_ordered=localdate()).exists():
                messages.error(request, f"You've already ordered {cart_item.product.name} today.")
                continue

            # Create the order
            order = Order.objects.create(user=user, order_id=f"ORD-{uuid.uuid4().hex[:8]}")
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
                total_price=cart_item.total_price(),
                instruction=instructions.get(str(cart_item.id), "")
            )
            cart_item.delete()  # Remove the item from the cart

        messages.success(request, "Your order has been placed successfully.")
        return redirect('manager_dashboard')

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'current_date': current_date,
        'customers': customers
    })


# API to update cart item quantity
@csrf_exempt
def update_cart_item(request):
    if request.method == "POST":
        data = json.loads(request.body)
        item_id = data.get('item_id')
        new_quantity = data.get('quantity')

        try:
            # Update the cart item
            cart_item = Cart.objects.get(id=item_id, user=request.user)
            cart_item.quantity = new_quantity
            cart_item.save()

            # Return success response with updated data
            return JsonResponse({'success': True, 'quantity': cart_item.quantity, 'total_price': cart_item.total_price()})

        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


# Order placed confirmation page
@login_required
def order_placed(request):
    return render(request, 'order_placed.html')


# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')


# views.py
from django.shortcuts import render, redirect
from .models import Cart, Order, OrderItem  # Update if needed

@login_required
def place_order(request):
    if request.method == 'POST':
        selected_items = request.POST.getlist('selected_items')
        
        # Fetch user
        user = request.user
        order_date = request.POST.get("order_date", now().date())

        # Create the order
        order = Order.objects.create(user=user, date_ordered=localdate(), order_id=generate_order_id())

        for item_id in selected_items:
            item = get_object_or_404(Cart, id=item_id)  # Replace CartItem if it's another model
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.discounted_price(),
                total_price=item.total_price()
            )

        return redirect('manager_dashboard')  # Redirect to manager dashboard after order
    else:
        return render(request, 'cart.html')  # If not POST, show the cart page

