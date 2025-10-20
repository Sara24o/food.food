from django.urls import path
from .views import signup_view, profile_view, smart_redirect, vendor_dashboard, vendor_orders, vendor_menu_management, vendor_add_menu_item, vendor_edit_menu_item


urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('profile/', profile_view, name='profile'),
    path('smart-redirect/', smart_redirect, name='smart-redirect'),
    path('vendor/dashboard/', vendor_dashboard, name='vendor-dashboard'),
    path('vendor/orders/', vendor_orders, name='vendor-orders'),
    path('vendor/menu/<int:restaurant_id>/', vendor_menu_management, name='vendor-menu'),
    path('vendor/menu/<int:restaurant_id>/add/', vendor_add_menu_item, name='vendor-add-menu-item'),
    path('vendor/menu/<int:restaurant_id>/edit/<int:menu_item_id>/', vendor_edit_menu_item, name='vendor-edit-menu-item'),
]


