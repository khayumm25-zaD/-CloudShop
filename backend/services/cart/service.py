"""Cart Service business logic."""

from typing import Optional
from sqlalchemy.orm import Session
from .repository import CartRepository, WishlistRepository
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class CartService:
    """Business logic for shopping cart."""

    @staticmethod
    def get_cart(db: Session, user_id: str):
        """Get user's cart."""
        cart = CartRepository.get_cart(db, user_id)
        return cart

    @staticmethod
    def add_to_cart(
        db: Session,
        user_id: str,
        product_id: str,
        quantity: int,
        price: float,
    ):
        """Add item to cart."""
        item = CartRepository.add_item(
            db=db,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            price=price,
        )
        cart = CartRepository.get_cart(db, user_id)
        logger.info(f"Item added to cart for user: {user_id}")
        return cart

    @staticmethod
    def update_cart_item(
        db: Session,
        item_id: str,
        quantity: int,
    ):
        """Update cart item quantity."""
        CartRepository.update_item(db, item_id, quantity)
        logger.info(f"Cart item updated: {item_id}")

    @staticmethod
    def remove_from_cart(db: Session, item_id: str):
        """Remove item from cart."""
        CartRepository.remove_item(db, item_id)
        logger.info(f"Item removed from cart: {item_id}")

    @staticmethod
    def clear_cart(db: Session, user_id: str):
        """Clear user's cart."""
        CartRepository.clear_cart(db, user_id)
        logger.info(f"Cart cleared for user: {user_id}")


class WishlistService:
    """Business logic for wishlist."""

    @staticmethod
    def get_wishlist(db: Session, user_id: str):
        """Get user's wishlist."""
        return WishlistRepository.get_wishlist(db, user_id)

    @staticmethod
    def add_to_wishlist(
        db: Session,
        user_id: str,
        product_id: str,
    ):
        """Add item to wishlist."""
        WishlistRepository.add_item(db, user_id, product_id)
        wishlist = WishlistRepository.get_wishlist(db, user_id)
        logger.info(f"Item added to wishlist for user: {user_id}")
        return wishlist

    @staticmethod
    def remove_from_wishlist(db: Session, item_id: str):
        """Remove item from wishlist."""
        WishlistRepository.remove_item(db, item_id)
        logger.info(f"Item removed from wishlist: {item_id}")
