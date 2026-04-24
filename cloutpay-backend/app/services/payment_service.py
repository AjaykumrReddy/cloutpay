import hashlib
import hmac
import os

from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentOrder
from app.models.users import User
from app.services.razorpay_service import client


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, user_id: int | None, amount: int):
        if not isinstance(amount, int):
            raise ValueError("Amount must be an integer")
        if amount < 10:
            raise ValueError("Minimum amount is Rs 10")

        razorpay_order = client.order.create({
            "amount": amount * 100,
            "currency": "INR"
        })

        order = PaymentOrder(
            user_id=user_id,
            razorpay_order_id=razorpay_order["id"],
            amount=amount,
            status="created"
        )

        self.db.add(order)
        self.db.flush()

        return {
            "order_id": razorpay_order["id"],
            "amount": amount * 100,
            "currency": "INR"
        }

    def verify_payment(self, data: dict, user_id: int | None = None) -> tuple[Payment, bool]:
        order_id = data["razorpay_order_id"]
        payment_id = data["razorpay_payment_id"]
        signature = data["razorpay_signature"]
        is_anonymous = data.get("anonymous") in (True, "true", "True", "1")

        body = f"{order_id}|{payment_id}"
        expected = hmac.new(
            os.getenv("RAZORPAY_KEY_SECRET", "").encode("utf-8"),
            body.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if expected != signature:
            raise ValueError("Invalid payment signature")

        order = self.db.query(PaymentOrder).filter_by(
            razorpay_order_id=order_id
        ).first()

        if not order:
            raise ValueError("Order not found")

        if order.status == "paid":
            existing = self.db.query(Payment).filter_by(order_id=order.id).first()
            if existing:
                return existing, False

        if is_anonymous:
            user_name = "Anonymous"
        elif user_id:
            user = self.db.query(User).filter_by(id=user_id).first()
            user_name = (user.display_name or user.phone_number) if user else "Anonymous"
        else:
            user_name = data.get("user_name") or "Anonymous"

        order.status = "paid"

        payment = Payment(
            order_id=order.id,
            razorpay_payment_id=payment_id,
            amount=order.amount,
            user_name=user_name
        )

        self.db.add(payment)
        self.db.flush()

        return payment, True
