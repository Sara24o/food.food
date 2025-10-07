from django.urls import path
from .views import splash_view, RestaurantListView, RestaurantDetailView, restaurant_menu


urlpatterns = [
    path('splash/', splash_view, name='splash'),
    path('', RestaurantListView.as_view(), name='restaurant-list'),
    path('<slug:slug>/', RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('<slug:slug>/menu/', restaurant_menu, name='restaurant-menu'),
]


