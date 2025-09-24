from django.db import models
from django.utils import timezone
from accounts.models import Customer
from restaurants.models import Restaurant, MenuItem


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_PREPARING = "preparing"
    STATUS_ON_THE_WAY = "on_the_way"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_PREPARING, "Preparing"),
        (STATUS_ON_THE_WAY, "On the way"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    delivery_address = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.user.username}"

    def recalculate_total(self):
        subtotal = sum(item.quantity * item.price for item in self.items.all())
        self.total_amount = subtotal + (self.restaurant.delivery_fee or 0)
        self.save(update_fields=["total_amount"]) 


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

# Create your models here.
