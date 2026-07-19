"""Order Service - Order processing and tracking."""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from backend.shared.models import BaseModel


class OrderStatus(str, PyEnum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, PyEnum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(BaseModel):
    """Order model."""

    __tablename__ = "orders"
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_status", "status"),
        Index("idx_order_number", "order_number", unique=True),
    )

    order_number = Column(String(50), nullable=False, unique=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Pricing
    subtotal = Column(Float, nullable=False)
    tax = Column(Float, default=0.0)
    shipping = Column(Float, default=0.0)
    total = Column(Float, nullable=False)
    
    # Shipping information
    shipping_address = Column(Text, nullable=False)
    billing_address = Column(Text, nullable=False)
    
    # Additional info
    notes = Column(Text, nullable=True)
    tracking_number = Column(String(100), nullable=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.order_number}>"


class OrderItem(BaseModel):
    """Order item model."""

    __tablename__ = "order_items"
    __table_args__ = (
        Index("idx_order_id", "order_id"),
        Index("idx_product_id", "product_id"),
    )

    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    sku = Column(String(50), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="items")

    def __repr__(self):
        return f"<OrderItem {self.product_name}>"


class Payment(BaseModel):
    """Payment model."""

    __tablename__ = "payments"
    __table_args__ = (
        Index("idx_order_id", "order_id"),
        Index("idx_transaction_id", "transaction_id"),
    )

    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    transaction_id = Column(String(100), nullable=False, unique=True, index=True)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String(50), nullable=False)  # credit_card, debit_card, paypal, etc.
    metadata = Column(Text, nullable=True)  # JSON metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    order = relationship("Order", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.transaction_id}>"
