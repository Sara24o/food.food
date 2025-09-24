from django.contrib import admin
from .models import Customer, Vendor


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "phone")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("restaurant_name", "user", "is_active")

# Register your models here.
