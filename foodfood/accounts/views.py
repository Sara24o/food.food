from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from .forms import SignupForm, CustomerProfileForm, MenuItemForm
from .models import Customer, Vendor

# Configuration du logger
logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    """Vue de connexion personnalisée avec logs détaillés"""
    
    def get(self, request, *args, **kwargs):
        print("=== GET LOGIN PAGE ===")
        logger.info("=== GET LOGIN PAGE ===")
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        print("=== TENTATIVE DE CONNEXION ===")
        print(f"Username reçu: '{request.POST.get('username', '')}'")
        print(f"Password reçu: {'*' * len(request.POST.get('password', ''))}")
        
        logger.info(f"=== TENTATIVE DE CONNEXION ===")
        logger.info(f"Username reçu: '{request.POST.get('username', '')}'")
        logger.info(f"Password reçu: {'*' * len(request.POST.get('password', ''))}")
        
        # Vérifier si l'utilisateur existe
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username:
            print("Username vide")
            logger.warning("Username vide")
            messages.error(request, "Username is required.")
            return super().post(request, *args, **kwargs)
            
        if not password:
            print("Password vide")
            logger.warning("Password vide")
            messages.error(request, "Password is required.")
            return super().post(request, *args, **kwargs)
        
        # Vérifier si l'utilisateur existe dans la base
        try:
            from django.contrib.auth.models import User
            user = User.objects.get(username=username)
            print(f"Utilisateur trouvé: {user.username}, Active: {user.is_active}")
            logger.info(f"Utilisateur trouvé: {user.username}, Active: {user.is_active}")
        except User.DoesNotExist:
            print(f"Utilisateur '{username}' n'existe pas")
            logger.error(f"Utilisateur '{username}' n'existe pas")
            messages.error(request, f"User '{username}' does not exist.")
            return super().post(request, *args, **kwargs)
        
        # Tester l'authentification
        print(f"Test d'authentification pour '{username}'")
        logger.info(f"Test d'authentification pour '{username}'")
        user = authenticate(username=username, password=password)
        
        if user is not None:
            print(f"Authentification RÉUSSIE pour '{username}'")
            print(f"User: {user.username}, Active: {user.is_active}, Staff: {user.is_staff}")
            logger.info(f"Authentification RÉUSSIE pour '{username}'")
            logger.info(f"User: {user.username}, Active: {user.is_active}, Staff: {user.is_staff}")
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('smart-redirect')
        else:
            print(f"Authentification ÉCHOUÉE pour '{username}'")
            print("Mot de passe incorrect ou utilisateur inactif")
            logger.error(f"Authentification ÉCHOUÉE pour '{username}'")
            logger.error("Mot de passe incorrect ou utilisateur inactif")
            messages.error(request, "Invalid username or password.")
            return super().post(request, *args, **kwargs)


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
            return redirect('menu-list')
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
    return redirect('menu-list')


@login_required
def vendor_dashboard(request):
    """Vendor dashboard with comprehensive analytics"""
    try:
        vendor = Vendor.objects.get(user=request.user)
        restaurants = vendor.restaurants.all()
        
        # Import models
        from orders.models import Order, OrderItem
        from restaurants.models import MenuItem
        
        # === ANALYTICS TEMPORELLES ===
        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Commandes par période
        orders_today = Order.objects.filter(
            restaurant__vendor=vendor,
            created_at__date=today
        )
        orders_week = Order.objects.filter(
            restaurant__vendor=vendor,
            created_at__gte=week_ago
        )
        orders_month = Order.objects.filter(
            restaurant__vendor=vendor,
            created_at__gte=month_ago
        )
        
        # === MÉTRIQUES FINANCIÈRES ===
        revenue_today = orders_today.aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_week = orders_week.aggregate(total=Sum('total_amount'))['total'] or 0
        revenue_month = orders_month.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # === MÉTRIQUES DE COMMANDES ===
        orders_count_today = orders_today.count()
        orders_count_week = orders_week.count()
        orders_count_month = orders_month.count()
        
        # Panier moyen
        avg_order_value_today = orders_today.aggregate(avg=Avg('total_amount'))['avg'] or 0
        avg_order_value_week = orders_week.aggregate(avg=Avg('total_amount'))['avg'] or 0
        avg_order_value_month = orders_month.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # === ANALYTICS PAR RESTAURANT ===
        restaurant_stats = []
        for restaurant in restaurants:
            restaurant_orders = Order.objects.filter(restaurant=restaurant)
            restaurant_orders_month = restaurant_orders.filter(created_at__gte=month_ago)
            
            stats = {
                'restaurant': restaurant,
                'total_orders': restaurant_orders.count(),
                'orders_this_month': restaurant_orders_month.count(),
                'revenue_this_month': restaurant_orders_month.aggregate(total=Sum('total_amount'))['total'] or 0,
                'avg_rating': restaurant.rating,
                'is_open': restaurant.is_open,
                'menu_items_count': restaurant.menu_items.count(),
                'available_items': restaurant.menu_items.filter(is_available=True).count(),
            }
            restaurant_stats.append(stats)
        
        # === PLATS LES PLUS VENDUS ===
        top_menu_items = OrderItem.objects.filter(
            order__restaurant__vendor=vendor,
            order__created_at__gte=month_ago
        ).values(
            'menu_item__name', 
            'menu_item__restaurant__name'
        ).annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('price')
        ).order_by('-total_quantity')[:10]
        
        # === COMMANDES RÉCENTES ===
        recent_orders = Order.objects.filter(
            restaurant__vendor=vendor
        ).order_by('-created_at')[:10]
        
        # === STATUTS DES COMMANDES ===
        order_status_stats = Order.objects.filter(
            restaurant__vendor=vendor,
            created_at__gte=month_ago
        ).values('status').annotate(count=Count('status'))
        
        # === TENDANCES HEBDOMADAIRES ===
        weekly_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            day_orders = Order.objects.filter(
                restaurant__vendor=vendor,
                created_at__date=date
            )
            weekly_data.append({
                'date': date,
                'orders': day_orders.count(),
                'revenue': day_orders.aggregate(total=Sum('total_amount'))['total'] or 0
            })
        weekly_data.reverse()  # Du plus ancien au plus récent
        
        # === PERFORMANCE GÉNÉRALE ===
        total_customers = Order.objects.filter(
            restaurant__vendor=vendor
        ).values('customer').distinct().count()
        
        repeat_customers = Order.objects.filter(
            restaurant__vendor=vendor
        ).values('customer').annotate(
            order_count=Count('id')
        ).filter(order_count__gt=1).count()
        
        customer_retention = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        context = {
            'vendor': vendor,
            'restaurants': restaurants,
            'recent_orders': recent_orders,
            
            # Métriques temporelles
            'revenue_today': revenue_today,
            'revenue_week': revenue_week,
            'revenue_month': revenue_month,
            'orders_count_today': orders_count_today,
            'orders_count_week': orders_count_week,
            'orders_count_month': orders_count_month,
            'avg_order_value_today': avg_order_value_today,
            'avg_order_value_week': avg_order_value_week,
            'avg_order_value_month': avg_order_value_month,
            
            # Analytics par restaurant
            'restaurant_stats': restaurant_stats,
            
            # Plats populaires
            'top_menu_items': top_menu_items,
            
            # Statuts des commandes
            'order_status_stats': order_status_stats,
            
            # Tendances
            'weekly_data': weekly_data,
            
            # Performance
            'total_customers': total_customers,
            'repeat_customers': repeat_customers,
            'customer_retention': customer_retention,
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
