from django.urls import path
from .views import upi_checkout, verify_payment, cod_confirm


urlpatterns = [
    path('upi/<int:order_id>/', upi_checkout, name='upi-checkout'),
    path('verify/', verify_payment, name='payment-verify'),
    path('cod/<int:order_id>/', cod_confirm, name='cod-confirm'),
]


