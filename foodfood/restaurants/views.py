from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Restaurant, MenuItem


def splash_view(request):
    """Splash screen for first-time visitors"""
    return render(request, 'splash.html')


class MenuListView(ListView):
    """Display all menu items from all restaurants on homepage"""
    model = MenuItem
    template_name = 'restaurants/menu_list.html'
    context_object_name = 'menu_items'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().filter(is_available=True).select_related('restaurant')
        
        # Search filters
        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')
        
        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(restaurant__name__icontains=q)
            )
        
        if category:
            qs = qs.filter(category=category)
            
        if price_min:
            try:
                qs = qs.filter(price__gte=float(price_min))
            except ValueError:
                pass
                
        if price_max:
            try:
                qs = qs.filter(price__lte=float(price_max))
            except ValueError:
                pass
        
        return qs.order_by('restaurant__name', 'category', 'name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '').strip()
        ctx['category'] = self.request.GET.get('category', '')
        ctx['price_min'] = self.request.GET.get('price_min', '')
        ctx['price_max'] = self.request.GET.get('price_max', '')
        ctx['categories'] = MenuItem.Category.choices
        return ctx


class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurants/list.html'
    context_object_name = 'restaurants'
    paginate_by = 12

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        cuisine = self.request.GET.get('cuisine')
        is_open = self.request.GET.get('open')
        if q:
            # Search across restaurants and their menu items
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(menu_items__name__icontains=q)
                | Q(menu_items__description__icontains=q)
                | Q(menu_items__category__icontains=q)
            ).distinct()
        if is_open == '1':
            qs = qs.filter(is_open=True)
        return qs.order_by('-rating', 'name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '').strip()
        ctx['open'] = self.request.GET.get('open', '')
        return ctx


class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurants/detail.html'
    context_object_name = 'restaurant'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


def restaurant_menu(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    items = restaurant.menu_items.filter(is_available=True)
    return render(request, 'restaurants/menu.html', {"restaurant": restaurant, "items": items})

# Create your views here.