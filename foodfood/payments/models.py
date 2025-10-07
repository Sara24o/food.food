from django.db import models
from orders.models import Order


class Payment(models.Model):
    METHOD_CARD = "card"
    METHOD_PAYPAL = "paypal"
    METHOD_COD = "cod"
    METHOD_CHOICES = [
        (METHOD_CARD, "Card"),
        (METHOD_PAYPAL, "PayPal"),
        (METHOD_COD, "Cash on Delivery"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order_id} - {self.status}"

# Create your models here.
