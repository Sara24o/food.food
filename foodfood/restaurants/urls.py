from django.urls import path
from .views import RestaurantListView, RestaurantDetailView, restaurant_menu


urlpatterns = [
    path('', RestaurantListView.as_view(), name='restaurant-list'),
    path('<slug:slug>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('<slug:slug>/menu/', restaurant_menu, name='restaurant-menu'),
]


