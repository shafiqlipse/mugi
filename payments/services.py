# payments/services.py
import re, time, random, requests, logging
from django.conf import settings
from django.db import transaction as db_transaction
from .models import Payment

airtel_logger = logging.getLogger("airtel")

def generate_transaction_id():
    for _ in range(5):  # retry on the rare collision instead of trusting luck
        timestamp_part = int(time.time() * 1000) % 10_000_000
        random_part = random.randint(10_000, 99_999)
        tx_id = f"{timestamp_part:07d}{random_part}"
        if not Payment.objects.filter(transaction_id=tx_id).exists():
            return tx_id
    raise RuntimeError("Could not generate a unique transaction ID")


def get_airtel_token():
    try:
        response = requests.post(
            "https://openapi.airtel.ug/auth/oauth2/token",
            json={
                "client_id": settings.AIRTEL_MONEY_CLIENT_ID,
                "client_secret": settings.AIRTEL_MONEY_CLIENT_SECRET,
                "grant_type": "client_credentials",
            },
            headers={"Content-Type": "application/json", "Accept": "*/*"},
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        airtel_logger.error(f"Airtel token failed: {response.status_code} {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        airtel_logger.error(f"Airtel token request error: {e}")
        return None


def format_msisdn(phone):
    digits = re.sub(r"\D", "", str(phone))
    return digits[1:] if digits.startswith("0") else digits


def initiate_airtel_payment(payment: Payment):
    """Takes an already-created Payment, pushes it to Airtel, returns (success, response)."""
    token = get_airtel_token()
    if not token:
        return False, {"error": "Failed to get authentication token"}

    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "X-Country": "UG",
        "X-Currency": "UGX",
        "Authorization": f"Bearer {token}",
        "x-signature": settings.AIRTEL_API_SIGNATURE,
        "x-key": settings.AIRTEL_API_KEY,
    }
    payload = {
        "reference": str(payment.transaction_id),
        "subscriber": {
            "country": "UG", "currency": "UGX",
            "msisdn": format_msisdn(payment.phone_number),
        },
        "transaction": {
            "amount": str(payment.amount),
            "country": "UG", "currency": "UGX",
            "id": payment.transaction_id,
        },
    }

    try:
        response = requests.post(
            "https://openapi.airtel.ug/merchant/v2/payments/",
            json=payload, headers=headers, timeout=(5, 30),
        )
        airtel_logger.info(f"Airtel Payment Response ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        airtel_logger.error(f"Airtel payment request failed: {e}")
        return False, {"error": str(e)}

    return response.status_code == 200, response


def create_and_initiate_payment(payment_type, amount, phone_number, related_obj_setter=None):
    """
    related_obj_setter: callable(payment) -> links the payment to the calling
    app's model, e.g. lambda p: setattr(trainee, 'payment', p) or edit_request.save()
    """
    with db_transaction.atomic():
        payment = Payment.objects.create(
            transaction_id=generate_transaction_id(),
            payment_type=payment_type,
            amount=amount,
            phone_number=phone_number,
            status="PENDING",
        )
        if related_obj_setter:
            related_obj_setter(payment)

    success, response = initiate_airtel_payment(payment)
    if not success:
        payment.status = "FAILED"
        payment.save(update_fields=["status"])
    return payment, success, response