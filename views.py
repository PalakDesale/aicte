from django.shortcuts import render, get_object_or_404, redirect
from .models import Cook, Dish
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def home(request):
    featured_dishes = Dish.objects.filter(is_available=True).select_related('cook')[:6]
    return render(request, 'marketplace/index.html', {'featured_dishes': featured_dishes})

def explore(request):
    query = request.GET.get('q', '')
    dishes = Dish.objects.filter(is_available=True).select_related('cook')
    
    if query:
        dishes = dishes.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(cook__name__icontains=query) |
            Q(cook__specialty__icontains=query)
        )
    
    return render(request, 'marketplace/explore.html', {'dishes': dishes, 'query': query})

def cook_detail(request, pk):
    cook = get_object_or_404(Cook, pk=pk)
    dishes = cook.dishes.filter(is_available=True)
    return render(request, 'marketplace/cook_detail.html', {'cook': cook, 'dishes': dishes})

def add_to_cart(request, dish_id):
    cart = request.session.get('cart', {})
    cart[str(dish_id)] = cart.get(str(dish_id), 0) + 1
    request.session['cart'] = cart
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    
    dishes_to_remove = []
    
    for dish_id, quantity in cart.items():
        try:
            dish = Dish.objects.get(id=dish_id)
            total_price += dish.price * quantity
            cart_items.append({
                'dish': dish,
                'quantity': quantity,
                'subtotal': dish.price * quantity
            })
        except Dish.DoesNotExist:
            dishes_to_remove.append(dish_id)
            
    # Remove invalid items from session
    if dishes_to_remove:
        for dish_id in dishes_to_remove:
            del cart[dish_id]
        request.session['cart'] = cart
    
    return render(request, 'marketplace/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def remove_from_cart(request, dish_id):
    cart = request.session.get('cart', {})
    if str(dish_id) in cart:
        del cart[str(dish_id)]
        request.session['cart'] = cart
    return redirect('view_cart')

def update_cart(request, dish_id, action):
    cart = request.session.get('cart', {})
    dish_id_str = str(dish_id)
    
    if dish_id_str in cart:
        if action == 'add':
            cart[dish_id_str] += 1
        elif action == 'remove':
            cart[dish_id_str] -= 1
            if cart[dish_id_str] <= 0:
                del cart[dish_id_str]
    
    request.session['cart'] = cart
    return redirect('view_cart')

from .models import Order, OrderItem

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    if request.method == 'POST':
        customer_name = request.POST.get('name')
        customer_phone = request.POST.get('phone')
        customer_address = request.POST.get('address')
        scheduled_time = request.POST.get('scheduled_time')
        servings_count = request.POST.get('servings_count')
        special_instructions = request.POST.get('special_instructions')

        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            user=request.user if request.user.is_authenticated else None,
            scheduled_time=parse_datetime(scheduled_time) if scheduled_time else None,
            servings_count=int(servings_count) if servings_count else 1,
            special_instructions=special_instructions,
            payment_method=request.POST.get('payment_method', 'COD'),
            payment_status='Paid' if request.POST.get('payment_method') == 'Online' else 'Pending'
        )

        for dish_id, quantity in cart.items():
            dish = get_object_or_404(Dish, id=dish_id)
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=quantity,
                price=dish.price
            )
        
        # Clear cart
        request.session['cart'] = {}
        return render(request, 'marketplace/order_success.html', {'order': order})

    return render(request, 'marketplace/checkout.html')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'marketplace/order_history.html', {'orders': orders})

@login_required
def cancel_order(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk, user=request.user)
        if order.status == 'Pending':
            order.status = 'Cancelled'
            order.save()
    return redirect('order_history')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Explicitly set backend for auto-login after user creation
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'marketplace/signup.html', {'form': form})
