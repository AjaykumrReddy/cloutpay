import uuid
from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentOrder
from app.models.users import User
from app.services.cashfree_service import create_cashfree_order, get_cashfree_order
from app.services.streak_service import update_streak


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, user_id: int | None, amount: int, customer_phone: str = "9999999999", guest_session_id: str | None = None):
        if amount < 1:
            raise ValueError("Minimum amount is Rs 1")

        # Generate a unique order_id for Cashfree
        cf_order_id = f"cloutpay_{uuid.uuid4().hex[:16]}"

        # Get customer details if logged in
        customer_name = "CloutPay User"
        if user_id:
            user = self.db.query(User).filter_by(id=user_id).first()
            if user:
                customer_phone = user.phone_number or customer_phone
                customer_name = user.display_name or customer_name

        cf_response = create_cashfree_order(
            order_id=cf_order_id,
            amount=float(amount),
            customer_id=str(user_id or f"guest_{uuid.uuid4().hex[:8]}"),
            customer_phone=customer_phone,
            customer_name=customer_name,
        )
        print(f"cf_response: {cf_response}")

        payment_session_id = cf_response.get("payment_session_id")

        order = PaymentOrder(
            user_id=user_id,
            cf_order_id=cf_order_id,
            payment_session_id=payment_session_id,
            guest_session_id=guest_session_id if not user_id else None,
            amount=amount,
            status="created",
        )
        self.db.add(order)
        self.db.flush()

        return {
            "cf_order_id": cf_order_id,
            "payment_session_id": payment_session_id,
            "amount": amount,
        }

    def verify_payment(self, cf_order_id: str, user_id: int | None, user_name_override: str | None = None, anonymous: bool = False) -> tuple[Payment, bool]:
        # Fetch order status from Cashfree
        cf_order = get_cashfree_order(cf_order_id)
        order_status = cf_order.get("order_status", "")

        if order_status != "PAID":
            raise ValueError(f"Payment not completed. Status: {order_status}")

        # Get our local order record
        order = self.db.query(PaymentOrder).filter_by(cf_order_id=cf_order_id).first()
        if not order:
            raise ValueError("Order not found")

        # Prevent duplicate processing
        if order.status == "paid":
            existing = self.db.query(Payment).filter_by(order_id=order.id).first()
            if existing:
                return existing, False

        # Get cf_payment_id from payments list
        payments_data = cf_order.get("payments", [])
        cf_payment_id = None
        if isinstance(payments_data, list) and payments_data:
            cf_payment_id = str(payments_data[0].get("cf_payment_id", ""))
        if not cf_payment_id:
            cf_payment_id = f"cf_{cf_order_id}"

        # Resolve user name
        if anonymous:
            user_name = "Anonymous"
        elif user_id:
            user = self.db.query(User).filter_by(id=user_id).first()
            user_name = (user.display_name or user.phone_number) if user else "Anonymous"
        else:
            user_name = user_name_override or "Anonymous"

        order.status = "paid"

        payment = Payment(
            order_id=order.id,
            cf_payment_id=cf_payment_id,
            payment_reference=cf_payment_id,
            amount=order.amount,
            user_name=user_name,
        )
        self.db.add(payment)
        self.db.flush()

        # Update streak for logged-in users
        if user_id:
            update_streak(self.db, user_id)

        return payment, True
