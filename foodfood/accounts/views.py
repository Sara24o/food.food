from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, CustomerProfileForm, MenuItemForm
from .models import Customer, Vendor


def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create customer profile with required phone
            phone = form.cleaned_data.get('phone')
            Customer.objects.create(user=user, phone=phone)
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect('/restaurants/')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {"form": form})


@login_required
def profile_view(request):
    customer, _ = Customer.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, instance=customer, user=request.user)
        if form.is_valid():
            customer = form.save()
            # update basic user fields
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            if email:
                request.user.email = email
            request.user.save()
            messages.success(request, "Profile updated.")
            return redirect('/accounts/profile/')
    else:
        form = CustomerProfileForm(instance=customer, user=request.user)
    return render(request, 'accounts/profile.html', {"form": form})


@login_required
def smart_redirect(request):
    """Redirect users based on their role after login"""
    try:
        if hasattr(request.user, 'vendor_profile') and request.user.vendor_profile:
            return redirect('vendor-dashboard')
    except Vendor.DoesNotExist:
        pass
    return redirect('restaurant-list')


@login_required
def vendor_dashboard(request):
    """Vendor dashboard showing restaurants and recent orders"""
    try:
        vendor = Vendor.objects.get(user=request.user)
        restaurants = vendor.restaurants.all()
        
        # Get recent orders from all vendor's restaurants
        from orders.models import Order
        recent_orders = Order.objects.filter(
            restaurant__vendor=vendor
        ).order_by('-created_at')[:5]
        
        context = {
            'vendor': vendor,
            'restaurants': restaurants,
            'recent_orders': recent_orders,
        }
        return render(request, 'accounts/vendor_dashboard.html', context)
    except Vendor.DoesNotExist:
        messages.error(request, "You are not a registered vendor.")
        return redirect('restaurant-list')


@login_required
def vendor_orders(request):
    """Vendor order management"""
    try:
        vendor = Vendor.objects.get(user=request.user)
    except Vendor.DoesNotExist:
        messages.error(request, "You are not a registered vendor.")
        return redirect('restaurant-list')
    
    from orders.models import Order
    
    # Handle POST requests for order status updates
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        
        try:
            order = Order.objects.get(id=order_id, restaurant__vendor=vendor)
            
            if action == 'accept':
                order.status = Order.STATUS_ACCEPTED
                order.save()
                messages.success(request, f"Order #{order.id} accepted successfully!")
            elif action == 'preparing':
                order.status = Order.STATUS_PREPARING
                order.save()
                messages.success(request, f"Order #{order.id} is now being prepared!")
            elif action == 'ready':
                order.status = Order.STATUS_ON_THE_WAY
                order.save()
                messages.success(request, f"Order #{order.id} is ready for delivery!")
            elif action == 'delivered':
                order.status = Order.STATUS_DELIVERED
                order.save()
                messages.success(request, f"Order #{order.id} has been delivered!")
            elif action == 'cancel':
                order.status = Order.STATUS_CANCELLED
                order.save()
                messages.success(request, f"Order #{order.id} has been cancelled!")
                
        except Order.DoesNotExist:
            messages.error(request, "Order not found or access denied.")
    
    # Get all orders for vendor's restaurants
    orders = Order.objects.filter(
        restaurant__vendor=vendor
    ).order_by('-created_at')
    
    # Calculate statistics
    total_orders = orders.count()
    pending_orders = orders.filter(status=Order.STATUS_PENDING).count()
    completed_orders = orders.filter(status=Order.STATUS_DELIVERED).count()
    in_progress_orders = orders.filter(
        status__in=[Order.STATUS_ACCEPTED, Order.STATUS_PREPARING, Order.STATUS_ON_THE_WAY]
    ).count()
    
    context = {
        'vendor': vendor,
        'orders': orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'in_progress_orders': in_progress_orders,
    }
    return render(request, 'accounts/vendor_orders.html', context)


@login_required
def vendor_menu_management(request, restaurant_id):
    """Vendor menu management for specific restaurant"""
    try:
        vendor = Vendor.objects.get(user=request.user)
        restaurant = vendor.restaurants.get(id=restaurant_id)
    except (Vendor.DoesNotExist, restaurant.DoesNotExist):
        messages.error(request, "Restaurant not found or access denied.")
        return redirect('vendor-dashboard')
    
    from restaurants.models import MenuItem
    menu_items = restaurant.menu_items.all()
    
    context = {
        'vendor': vendor,
        'restaurant': restaurant,
        'menu_items': menu_items,
    }
    return render(request, 'accounts/vendor_menu.html', context)


@login_required
def vendor_add_menu_item(request, restaurant_id):
    """Add new menu item for vendor's restaurant"""
    try:
        vendor = Vendor.objects.get(user=request.user)
        restaurant = vendor.restaurants.get(id=restaurant_id)
    except (Vendor.DoesNotExist, restaurant.DoesNotExist):
        messages.error(request, "Restaurant not found or access denied.")
        return redirect('vendor-dashboard')
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant
            menu_item.save()
            messages.success(request, f"Menu item '{menu_item.name}' added successfully!")
            return redirect('vendor-menu', restaurant_id=restaurant.id)
    else:
        form = MenuItemForm()
    
    context = {
        'vendor': vendor,
        'restaurant': restaurant,
        'form': form,
    }
    return render(request, 'accounts/vendor_add_menu_item.html', context)


@login_required
def vendor_edit_menu_item(request, restaurant_id, menu_item_id):
    """Edit existing menu item for vendor's restaurant"""
    try:
        vendor = Vendor.objects.get(user=request.user)
        restaurant = vendor.restaurants.get(id=restaurant_id)
        menu_item = restaurant.menu_items.get(id=menu_item_id)
    except (Vendor.DoesNotExist, restaurant.DoesNotExist, menu_item.DoesNotExist):
        messages.error(request, "Menu item not found or access denied.")
        return redirect('vendor-dashboard')
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Menu item '{menu_item.name}' updated successfully!")
            return redirect('vendor-menu', restaurant_id=restaurant.id)
    else:
        form = MenuItemForm(instance=menu_item)
    
    context = {
        'vendor': vendor,
        'restaurant': restaurant,
        'menu_item': menu_item,
        'form': form,
    }
    return render(request, 'accounts/vendor_edit_menu_item.html', context)



# Create your views here.
