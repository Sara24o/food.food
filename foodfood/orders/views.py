from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import Order, OrderItem
from restaurants.models import MenuItem, Restaurant
from accounts.models import Customer
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
class OrderListView(ListView):
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'


@method_decorator(login_required, name='dispatch')
class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'


def _get_cart(session):
    cart = session.get('cart')
    if not cart:
        cart = {"items": {}, "restaurant_id": None}
        session['cart'] = cart
    return cart


@login_required
def add_to_cart(request, menu_item_id):
    item = get_object_or_404(MenuItem, id=menu_item_id, is_available=True)
    cart = _get_cart(request.session)
    # Ensure cart is tied to one restaurant
    if cart["restaurant_id"] and cart["restaurant_id"] != item.restaurant_id:
        # reset cart if different restaurant
        cart = {"items": {}, "restaurant_id": item.restaurant_id}
    if not cart["restaurant_id"]:
        cart["restaurant_id"] = item.restaurant_id
    cart_items = cart["items"]
    cart_items[str(menu_item_id)] = cart_items.get(str(menu_item_id), 0) + 1
    request.session['cart'] = cart
    return redirect('cart-view')


@login_required
def remove_from_cart(request, menu_item_id):
    cart = _get_cart(request.session)
    cart_items = cart.get("items", {})
    key = str(menu_item_id)
    if key in cart_items:
        cart_items[key] -= 1
        if cart_items[key] <= 0:
            del cart_items[key]
        request.session['cart'] = cart
    return redirect('cart-view')


@login_required
def cart_view(request):
    cart = _get_cart(request.session)
    items = []
    subtotal = 0
    restaurant = None
    if cart["items"]:
        ids = [int(k) for k in cart["items"].keys()]
        qs = MenuItem.objects.filter(id__in=ids)
        for mi in qs:
            qty = cart["items"].get(str(mi.id), 0)
            line_total = mi.price * qty
            subtotal += line_total
            items.append({"menu_item": mi, "quantity": qty, "line_total": line_total})
        if cart["restaurant_id"]:
            restaurant = Restaurant.objects.filter(id=cart["restaurant_id"]).first()
    delivery_fee = restaurant.delivery_fee if restaurant else 0
    total = subtotal + (delivery_fee or 0)
    return render(request, 'orders/cart.html', {
        "cart_items": items,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": total,
        "restaurant": restaurant,
    })


@login_required
@transaction.atomic
def checkout_view(request):
    if request.method != 'POST':
        return redirect('cart-view')
    cart = _get_cart(request.session)
    if not cart["items"]:
        return redirect('cart-view')
    restaurant = get_object_or_404(Restaurant, id=cart["restaurant_id"])
    customer, _ = Customer.objects.get_or_create(user=request.user)
    if not customer.phone:
        messages.warning(request, "Please provide your phone number before checkout.")
        return redirect('/accounts/profile/')
    order = Order.objects.create(
        customer=customer,
        restaurant=restaurant,
        delivery_address=customer.address or 'Adresse non fournie',
        status=Order.STATUS_PENDING,
    )
    # create items
    ids = [int(k) for k in cart["items"].keys()]
    menu_items = {mi.id: mi for mi in MenuItem.objects.filter(id__in=ids)}
    for mid, qty in cart["items"].items():
        mi = menu_items.get(int(mid))
        if not mi:
            continue
        OrderItem.objects.create(order=order, menu_item=mi, quantity=qty, price=mi.price)
    order.recalculate_total()
    # clear cart
    request.session['cart'] = {"items": {}, "restaurant_id": None}
    return redirect('order-detail', pk=order.pk)


@login_required
def order_history(request):
    customer = Customer.objects.filter(user=request.user).first()
    orders = Order.objects.filter(customer=customer).order_by('-created_at') if customer else []
    return render(request, 'orders/history.html', {"orders": orders})

# Create your views here.
