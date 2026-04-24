from sqlalchemy.orm import Session
from app.models.payment import PaymentOrder, Payment
from app.services.razorpay_service import client
import hmac, hashlib, os


class PaymentService:

    def __init__(self, db: Session):
        self.db = db

    def create_order(self, user_id: int | None, amount: int):
        if amount < 10:
            raise ValueError("Minimum amount is ₹10")

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

    def verify_payment(self, data: dict) -> Payment:
        order_id = data["razorpay_order_id"]
        payment_id = data["razorpay_payment_id"]
        signature = data["razorpay_signature"]
        user_name = data.get("user_name") or "Anonymous"

        # Bug fix: hmac.new → hmac.new is invalid; correct is hmac.new
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

        # Idempotency: return existing payment instead of crashing
        if order.status == "paid":
            existing = self.db.query(Payment).filter_by(order_id=order.id).first()
            if existing:
                return existing

        order.status = "paid"

        payment = Payment(
            order_id=order.id,
            razorpay_payment_id=payment_id,
            amount=order.amount,
            user_name=user_name
        )

        self.db.add(payment)
        self.db.flush()

        return payment