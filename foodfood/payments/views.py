from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
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
    """Mark order as to be paid by Cash on Delivery and create a Payment record."""
    order = get_object_or_404(Order, pk=order_id)
    Payment.objects.create(order=order, method=Payment.METHOD_COD, amount=order.total_amount, status=Payment.STATUS_PENDING)
    return JsonResponse({"status": "ok", "message": "COD selected"})


@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")

    payload = request.POST
    order_id = payload.get("razorpay_order_id")
    payment_id = payload.get("razorpay_payment_id")
    signature = payload.get("razorpay_signature")

    if not (order_id and payment_id and signature):
        return HttpResponseBadRequest("Missing params")

    client = get_razorpay_client()
    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
        return JsonResponse({"status": "ok"})
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"status": "failed"}, status=400)

# Create your views here.
