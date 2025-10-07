from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Restaurant, MenuItem


def splash_view(request):
    """Splash screen for first-time visitors"""
    return render(request, 'splash.html')


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
        if cuisine:
            qs = qs.filter(cuisine_type=cuisine)
        if is_open == '1':
            qs = qs.filter(is_open=True)
        return qs.order_by('-rating', 'name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '').strip()
        ctx['cuisine'] = self.request.GET.get('cuisine', '')
        ctx['open'] = self.request.GET.get('open', '')
        ctx['cuisines'] = Restaurant.CuisineType.choices
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