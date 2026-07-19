"""Order Service repository."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid

from .models import Order, OrderItem, Payment, OrderStatus, PaymentStatus
from backend.shared.exceptions import ResourceNotFoundException, ConflictException
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class OrderRepository:
    """Repository for Order operations."""

    @staticmethod
    def _generate_order_number() -> str:
        """Generate unique order number."""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"

    @staticmethod
    def create(
        db: Session,
        user_id: str,
        items: List[dict],
        shipping_address: str,
        billing_address: str,
        subtotal: float,
        tax: float = 0.0,
        shipping: float = 0.0,
        notes: Optional[str] = None,
    ) -> Order:
        """Create a new order."""
        order = Order(
            order_number=OrderRepository._generate_order_number(),
            user_id=user_id,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            total=subtotal + tax + shipping,
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
        )
        db.add(order)
        db.flush()

        # Add items
        for item_data in items:
            item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                sku=item_data["sku"],
                quantity=item_data["quantity"],
                price=item_data["price"],
                total=item_data["quantity"] * item_data["price"],
            )
            db.add(item)

        db.commit()
        db.refresh(order)
        logger.info(f"Order created: {order.order_number}")
        return order

    @staticmethod
    def get_by_id(db: Session, order_id: str) -> Order:
        """Get order by ID."""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ResourceNotFoundException("Order", order_id)
        return order

    @staticmethod
    def get_by_order_number(db: Session, order_number: str) -> Order:
        """Get order by order number."""
        order = db.query(Order).filter(Order.order_number == order_number).first()
        if not order:
            raise ResourceNotFoundException("Order", order_number)
        return order

    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Order], int]:
        """Get user's orders."""
        q = db.query(Order).filter(Order.user_id == user_id)
        
        if status:
            q = q.filter(Order.status == status)
        
        total = q.count()
        orders = q.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
        return orders, total

    @staticmethod
    def update_status(
        db: Session,
        order_id: str,
        new_status: OrderStatus,
        tracking_number: Optional[str] = None,
    ) -> Order:
        """Update order status."""
        order = OrderRepository.get_by_id(db, order_id)
        order.status = new_status
        
        if tracking_number:
            order.tracking_number = tracking_number
        
        from datetime import datetime
        if new_status == OrderStatus.SHIPPED:
            order.shipped_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED:
            order.delivered_at = datetime.utcnow()
        
        db.commit()
        db.refresh(order)
        logger.info(f"Order status updated: {order_id} -> {new_status}")
        return order

    @staticmethod
    def cancel_order(db: Session, order_id: str) -> Order:
        """Cancel order."""
        order = OrderRepository.get_by_id(db, order_id)
        
        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ConflictException("Cannot cancel shipped/delivered order")
        
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        logger.info(f"Order cancelled: {order_id}")
        return order


class PaymentRepository:
    """Repository for Payment operations."""

    @staticmethod
    def create(
        db: Session,
        order_id: str,
        amount: float,
        payment_method: str,
        metadata: Optional[str] = None,
    ) -> Payment:
        """Create a new payment."""
        payment = Payment(
            order_id=order_id,
            transaction_id=f"TXN-{uuid.uuid4()}",
            amount=amount,
            payment_method=payment_method,
            metadata=metadata,
            status=PaymentStatus.PENDING,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)
        logger.info(f"Payment created: {payment.transaction_id}")
        return payment

    @staticmethod
    def get_by_id(db: Session, payment_id: str) -> Payment:
        """Get payment by ID."""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ResourceNotFoundException("Payment", payment_id)
        return payment

    @staticmethod
    def update_status(
        db: Session,
        payment_id: str,
        status: PaymentStatus,
    ) -> Payment:
        """Update payment status."""
        payment = PaymentRepository.get_by_id(db, payment_id)
        payment.status = status
        
        # Update order payment status
        order = payment.order
        if status == PaymentStatus.COMPLETED:
            order.payment_status = PaymentStatus.COMPLETED
            order.status = OrderStatus.CONFIRMED
        elif status == PaymentStatus.FAILED:
            order.payment_status = PaymentStatus.FAILED
        
        db.commit()
        db.refresh(payment)
        logger.info(f"Payment status updated: {payment_id} -> {status}")
        return payment
