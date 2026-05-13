import os
import hmac
import hashlib
import base64
import httpx


def _get_base_url() -> str:
    env = os.getenv("CASHFREE_ENV", "TEST")
    return (
        "https://api.cashfree.com/pg"
        if env == "PRODUCTION"
        else "https://sandbox.cashfree.com/pg"
    )


def _get_headers() -> dict:
    return {
        "x-api-version": "2023-08-01",
        "x-client-id": os.getenv("CASHFREE_APP_ID", ""),
        "x-client-secret": os.getenv("CASHFREE_SECRET_KEY", ""),
        "Content-Type": "application/json",
    }


def create_cashfree_order(
    order_id: str,
    amount: float,
    customer_id: str,
    customer_phone: str,
    customer_name: str = "CloutPay User",
) -> dict:
    payload = {
        "order_id": order_id,
        "order_amount": amount,
        "order_currency": "INR",
        "customer_details": {
            "customer_id": customer_id,
            "customer_phone": customer_phone,
            "customer_name": customer_name,
        },
    }
    webhook_url = os.getenv("CASHFREE_WEBHOOK_URL", "")
    if webhook_url:
        payload["order_meta"] = {"notify_url": webhook_url}

    response = httpx.post(
        f"{_get_base_url()}/orders",
        json=payload,
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response.json()


def get_cashfree_order(order_id: str) -> dict:
    response = httpx.get(
        f"{_get_base_url()}/orders/{order_id}",
        headers=_get_headers(),
    )
    response.raise_for_status()
    return response.json()


def verify_cashfree_webhook(raw_body: bytes, timestamp: str, signature: str) -> bool:
    secret = os.getenv("CASHFREE_SECRET_KEY", "")
    message = f"{timestamp}{raw_body.decode('utf-8')}"
    expected = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")
    return hmac.compare_digest(expected, signature)
