"""Order Service business logic."""

from typing import Optional, List
from sqlalchemy.orm import Session
from .repository import OrderRepository, PaymentRepository
from .models import OrderStatus, PaymentStatus
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class OrderService:
    """Business logic for orders."""

    @staticmethod
    def create_order(
        db: Session,
        user_id: str,
        items: List[dict],
        shipping_address: str,
        billing_address: str,
        subtotal: float,
        tax: float = 0.0,
        shipping: float = 0.0,
        notes: Optional[str] = None,
    ):
        """Create a new order."""
        order = OrderRepository.create(
            db=db,
            user_id=user_id,
            items=items,
            shipping_address=shipping_address,
            billing_address=billing_address,
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            notes=notes,
        )
        logger.info(f"Order created: {order.order_number}")
        return order

    @staticmethod
    def get_order(db: Session, order_id: str):
        """Get order details."""
        return OrderRepository.get_by_id(db, order_id)

    @staticmethod
    def get_user_orders(
        db: Session,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        """Get user's orders."""
        skip = (page - 1) * page_size
        orders, total = OrderRepository.get_user_orders(
            db=db,
            user_id=user_id,
            status=status,
            skip=skip,
            limit=page_size,
        )
        total_pages = (total + page_size - 1) // page_size
        return {
            "orders": orders,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }

    @staticmethod
    def update_order_status(
        db: Session,
        order_id: str,
        status: str,
        tracking_number: Optional[str] = None,
    ):
        """Update order status."""
        order = OrderRepository.update_status(
            db=db,
            order_id=order_id,
            new_status=OrderStatus(status),
            tracking_number=tracking_number,
        )
        logger.info(f"Order status updated: {order_id}")
        return order

    @staticmethod
    def cancel_order(db: Session, order_id: str):
        """Cancel order."""
        order = OrderRepository.cancel_order(db, order_id)
        logger.info(f"Order cancelled: {order_id}")
        return order


class PaymentService:
    """Business logic for payments."""

    @staticmethod
    def create_payment(
        db: Session,
        order_id: str,
        amount: float,
        payment_method: str,
        metadata: Optional[str] = None,
    ):
        """Create a payment."""
        payment = PaymentRepository.create(
            db=db,
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            metadata=metadata,
        )
        logger.info(f"Payment created: {payment.transaction_id}")
        return payment

    @staticmethod
    def process_payment(
        db: Session,
        payment_id: str,
        status: str,
    ):
        """Process payment."""
        payment = PaymentRepository.update_status(
            db=db,
            payment_id=payment_id,
            status=PaymentStatus(status),
        )
        logger.info(f"Payment processed: {payment_id}")
        return payment
