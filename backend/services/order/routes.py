"""Order Service API routes."""

from fastapi import APIRouter, Depends, Query, status, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Optional

from .schemas import (
    OrderResponse,
    OrderDetailResponse,
    OrderItemResponse,
    CreateOrderRequest,
    UpdateOrderStatusRequest,
    PaymentResponse,
    SearchOrdersRequest,
)
from .service import OrderService, PaymentService
from backend.shared.deps import get_db, require_user
from backend.shared.security import TokenData
from backend.shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Create a new order from cart items",
)
async def create_order(
    request: CreateOrderRequest,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Create a new order."""
    try:
        # Calculate totals
        subtotal = sum(item.quantity * item.price for item in request.items)
        tax = subtotal * 0.1  # 10% tax
        shipping = 10.0 if subtotal > 0 else 0.0

        order = OrderService.create_order(
            db=db,
            user_id=current_user.user_id,
            items=[item.dict() for item in request.items],
            shipping_address=request.shipping_address,
            billing_address=request.billing_address,
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            notes=request.notes,
        )
        return OrderResponse.from_attributes(order)
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order",
        )


@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse,
    summary="Get order details",
    description="Get detailed information about a specific order",
)
async def get_order(
    order_id: str = Path(...),
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get order details."""
    try:
        order = OrderService.get_order(db, order_id)
        
        # Verify ownership
        if order.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this order",
            )
        
        return OrderDetailResponse.from_attributes(order)
    except Exception as e:
        logger.error(f"Error fetching order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch order",
        )


@router.get(
    "",
    response_model=dict,
    summary="Get user's orders",
    description="Get list of user's orders",
)
async def get_user_orders(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get user's orders."""
    try:
        result = OrderService.get_user_orders(
            db=db,
            user_id=current_user.user_id,
            status=status,
            page=page,
            page_size=page_size,
        )
        return {
            "orders": [OrderResponse.from_attributes(o) for o in result["orders"]],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "has_next": result["has_next"],
            "has_previous": result["has_previous"],
        }
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch orders",
        )


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status",
    description="Update order status (admin only)",
)
async def update_order_status(
    order_id: str = Path(...),
    request: UpdateOrderStatusRequest = None,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Update order status."""
    try:
        # Check admin privileges
        if "admin" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
        
        order = OrderService.update_order_status(
            db=db,
            order_id=order_id,
            status=request.status.value,
            tracking_number=request.tracking_number,
        )
        return OrderResponse.from_attributes(order)
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status",
        )


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancel order",
    description="Cancel a pending order",
)
async def cancel_order(
    order_id: str = Path(...),
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Cancel order."""
    try:
        order = OrderService.get_order(db, order_id)
        
        # Verify ownership
        if order.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this order",
            )
        
        order = OrderService.cancel_order(db, order_id)
        return {"message": "Order cancelled successfully", "order_id": order.id}
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order",
        )


@router.post(
    "/{order_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment",
    description="Create a payment for an order",
)
async def create_payment(
    order_id: str = Path(...),
    request: dict = None,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Create a payment."""
    try:
        order = OrderService.get_order(db, order_id)
        
        # Verify ownership
        if order.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized",
            )
        
        payment = PaymentService.create_payment(
            db=db,
            order_id=order_id,
            amount=order.total,
            payment_method=request.get("payment_method", "credit_card"),
        )
        return PaymentResponse.from_attributes(payment)
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment",
        )


@router.get(
    "/health",
    summary="Health check",
    description="Check if order service is healthy",
)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "order",
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )
