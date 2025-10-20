from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib import messages
from django.conf import settings
from orders.models import Order
import razorpay
from .models import Payment


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def upi_checkout(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    amount_paise = int(order.total_amount * 100) if hasattr(order, 'total_amount') else int(order.get_total() * 100)

    error_message = None
    rp_order_id = None

    try:
        key_id = settings.RAZORPAY_KEY_ID
        key_secret = settings.RAZORPAY_KEY_SECRET
        if not key_id or not key_secret or key_id.startswith("rzp_test_xxxxx"):
            raise razorpay.errors.BadRequestError("Razorpay test keys not configured")

        client = razorpay.Client(auth=(key_id, key_secret))
        rp_order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1,
        })
        rp_order_id = rp_order["id"]
    except Exception as e:
        error_message = str(e)

    context = {
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "rp_order_id": rp_order_id,
        "amount": amount_paise,
        "display_amount": amount_paise / 100,
        "order": order,
        "error_message": error_message,
    }
    return render(request, "payments/upi_checkout.html", context)


@csrf_exempt
def cod_confirm(request, order_id):
    """Mark order as Cash on Delivery, create Payment, and move order forward."""
    order = get_object_or_404(Order, pk=order_id)
    Payment.objects.update_or_create(
        order=order,
        defaults={
            "method": Payment.METHOD_COD,
            "amount": order.total_amount,
            "status": Payment.STATUS_PENDING,
        },
    )
    # Consider COD as accepted/preparing depending on your business flow
    if order.status == Order.STATUS_PENDING:
        order.status = Order.STATUS_ACCEPTED
        order.save(update_fields=["status"])
    messages.success(request, "Cash on Delivery confirmed. Your order is accepted.")
    # Redirect to order detail for better UX instead of returning JSON
    return redirect('order-detail', pk=order.pk)


@csrf_exempt
@require_POST
@transaction.atomic
def verify_payment(request):
    payload = request.POST
    rp_order_id = payload.get("razorpay_order_id")
    payment_id = payload.get("razorpay_payment_id")
    signature = payload.get("razorpay_signature")
    # We need the application Order primary key to relate payment back
    app_order_id = payload.get("app_order_id")

    if not (rp_order_id and payment_id and signature and app_order_id):
        return HttpResponseBadRequest("Missing params")

    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": rp_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })

        order = get_object_or_404(Order.objects.select_for_update(), pk=app_order_id)
        # Create or update a Payment record
        payment_obj, _ = Payment.objects.update_or_create(
            order=order,
            defaults={
                "method": Payment.METHOD_CARD,
                "amount": order.total_amount,
                "status": Payment.STATUS_SUCCESS,
                "transaction_id": payment_id,
            },
        )
        # Update order status to accepted or delivered depending on your flow
        if order.status in (Order.STATUS_PENDING, Order.STATUS_ACCEPTED):
            order.status = Order.STATUS_ACCEPTED
            order.save(update_fields=["status"])

        return JsonResponse({"status": "ok", "payment_id": payment_obj.id})
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"status": "failed"}, status=400)

# Create your views here.
