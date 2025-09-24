from django.urls import path
from .views import (
    OrderListView,
    OrderDetailView,
    cart_view,
    add_to_cart,
    remove_from_cart,
    checkout_view,
    order_history,
)


urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('cart/', cart_view, name='cart-view'),
    path('add/<int:menu_item_id>/', add_to_cart, name='add-to-cart'),
    path('remove/<int:menu_item_id>/', remove_from_cart, name='remove-from-cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('history/', order_history, name='order-history'),
]


