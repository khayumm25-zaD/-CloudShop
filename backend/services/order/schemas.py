"""Order Service schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OrderStatusEnum(str, Enum):
    """Order status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatusEnum(str, Enum):
    """Payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class OrderItemBase(BaseModel):
    """Order item base schema."""

    product_id: str
    product_name: str
    sku: str
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0)


class OrderItemCreate(OrderItemBase):
    """Create order item schema."""
    pass


class OrderItemResponse(OrderItemBase):
    """Order item response schema."""

    id: str
    order_id: str
    total: float
    created_at: datetime

    class Config:
        from_attributes = True


class CreateOrderRequest(BaseModel):
    """Create order request."""

    items: List[OrderItemCreate]
    shipping_address: str
    billing_address: str
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    """Payment response schema."""

    id: str
    transaction_id: str
    amount: float
    status: PaymentStatusEnum
    payment_method: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response schema."""

    id: str
    order_number: str
    user_id: str
    status: OrderStatusEnum
    payment_status: PaymentStatusEnum
    subtotal: float
    tax: float
    shipping: float
    total: float
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """Order detail with payments."""

    shipping_address: str
    billing_address: str
    tracking_number: Optional[str]
    notes: Optional[str]
    payments: List[PaymentResponse]


class UpdateOrderStatusRequest(BaseModel):
    """Update order status request."""

    status: OrderStatusEnum
    tracking_number: Optional[str] = None
    notes: Optional[str] = None


class SearchOrdersRequest(BaseModel):
    """Search orders request."""

    status: Optional[OrderStatusEnum] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
