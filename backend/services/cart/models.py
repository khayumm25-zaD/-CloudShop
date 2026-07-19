"""Cart Service - Shopping cart and wishlist management."""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.shared.models import BaseModel


class Cart(BaseModel):
    """Shopping cart model."""

    __tablename__ = "carts"
    __table_args__ = (
        Index("idx_user_id", "user_id", unique=True),
    )

    user_id = Column(String(36), nullable=False, unique=True, index=True)
    total_items = Column(Integer, default=0)
    total_price = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cart {self.user_id}>"


class CartItem(BaseModel):
    """Shopping cart item model."""

    __tablename__ = "cart_items"
    __table_args__ = (
        Index("idx_cart_id", "cart_id"),
        Index("idx_product_id", "product_id"),
    )

    cart_id = Column(String(36), ForeignKey("carts.id"), nullable=False)
    product_id = Column(String(36), nullable=False, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    cart = relationship("Cart", back_populates="items")

    def __repr__(self):
        return f"<CartItem {self.product_id}>"


class Wishlist(BaseModel):
    """Wishlist model."""

    __tablename__ = "wishlists"
    __table_args__ = (
        Index("idx_user_id", "user_id", unique=True),
    )

    user_id = Column(String(36), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Wishlist {self.user_id}>"


class WishlistItem(BaseModel):
    """Wishlist item model."""

    __tablename__ = "wishlist_items"
    __table_args__ = (
        Index("idx_wishlist_id", "wishlist_id"),
        Index("idx_product_id", "product_id"),
    )

    wishlist_id = Column(String(36), ForeignKey("wishlists.id"), nullable=False)
    product_id = Column(String(36), nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    wishlist = relationship("Wishlist", back_populates="items")

    def __repr__(self):
        return f"<WishlistItem {self.product_id}>"
