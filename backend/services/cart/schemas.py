"""Cart Service schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CartItemBase(BaseModel):
    """Cart item base schema."""

    product_id: str
    quantity: int = Field(1, ge=1)


class CartItemCreate(CartItemBase):
    """Create cart item schema."""
    pass


class CartItemResponse(CartItemBase):
    """Cart item response schema."""

    id: str
    cart_id: str
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Cart response schema."""

    id: str
    user_id: str
    items: List[CartItemResponse]
    total_items: int
    total_price: float
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class AddToCartRequest(BaseModel):
    """Add to cart request."""

    product_id: str
    quantity: int = Field(1, ge=1)
    price: float = Field(..., ge=0)


class UpdateCartItemRequest(BaseModel):
    """Update cart item request."""

    quantity: int = Field(..., ge=1)


class WishlistItemResponse(BaseModel):
    """Wishlist item response schema."""

    id: str
    product_id: str
    added_at: datetime

    class Config:
        from_attributes = True


class WishlistResponse(BaseModel):
    """Wishlist response schema."""

    id: str
    user_id: str
    items: List[WishlistItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True
