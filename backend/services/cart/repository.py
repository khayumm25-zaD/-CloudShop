"""Cart Service repository."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import Cart, CartItem, Wishlist, WishlistItem
from backend.shared.exceptions import ResourceNotFoundException, ConflictException
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class CartRepository:
    """Repository for Cart operations."""

    @staticmethod
    def get_or_create_cart(db: Session, user_id: str) -> Cart:
        """Get or create cart for user."""
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
            logger.info(f"Cart created for user: {user_id}")
        return cart

    @staticmethod
    def get_cart(db: Session, user_id: str) -> Cart:
        """Get user's cart."""
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            raise ResourceNotFoundException("Cart", user_id)
        return cart

    @staticmethod
    def add_item(
        db: Session,
        user_id: str,
        product_id: str,
        quantity: int,
        price: float,
    ) -> CartItem:
        """Add item to cart."""
        cart = CartRepository.get_or_create_cart(db, user_id)

        # Check if item already in cart
        existing_item = db.query(CartItem).filter(
            and_(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        ).first()

        if existing_item:
            existing_item.quantity += quantity
            item = existing_item
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                price=price,
            )
            db.add(item)

        # Update cart totals
        CartRepository._update_cart_totals(db, cart.id)
        db.commit()
        db.refresh(item)
        logger.info(f"Item added to cart: {product_id}")
        return item

    @staticmethod
    def update_item(
        db: Session,
        item_id: str,
        quantity: int,
    ) -> CartItem:
        """Update cart item quantity."""
        item = db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            raise ResourceNotFoundException("CartItem", item_id)

        item.quantity = quantity
        CartRepository._update_cart_totals(db, item.cart_id)
        db.commit()
        db.refresh(item)
        logger.info(f"Cart item updated: {item_id}")
        return item

    @staticmethod
    def remove_item(db: Session, item_id: str) -> None:
        """Remove item from cart."""
        item = db.query(CartItem).filter(CartItem.id == item_id).first()
        if not item:
            raise ResourceNotFoundException("CartItem", item_id)

        cart_id = item.cart_id
        db.delete(item)
        CartRepository._update_cart_totals(db, cart_id)
        db.commit()
        logger.info(f"Item removed from cart: {item_id}")

    @staticmethod
    def clear_cart(db: Session, user_id: str) -> None:
        """Clear user's cart."""
        cart = CartRepository.get_cart(db, user_id)
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        cart.total_items = 0
        cart.total_price = 0.0
        db.commit()
        logger.info(f"Cart cleared for user: {user_id}")

    @staticmethod
    def _update_cart_totals(db: Session, cart_id: str) -> None:
        """Update cart total items and price."""
        cart = db.query(Cart).filter(Cart.id == cart_id).first()
        if cart:
            items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
            cart.total_items = sum(item.quantity for item in items)
            cart.total_price = sum(item.quantity * item.price for item in items)


class WishlistRepository:
    """Repository for Wishlist operations."""

    @staticmethod
    def get_or_create_wishlist(db: Session, user_id: str) -> Wishlist:
        """Get or create wishlist for user."""
        wishlist = db.query(Wishlist).filter(Wishlist.user_id == user_id).first()
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            db.add(wishlist)
            db.commit()
            db.refresh(wishlist)
            logger.info(f"Wishlist created for user: {user_id}")
        return wishlist

    @staticmethod
    def add_item(
        db: Session,
        user_id: str,
        product_id: str,
    ) -> WishlistItem:
        """Add item to wishlist."""
        wishlist = WishlistRepository.get_or_create_wishlist(db, user_id)

        # Check if item already in wishlist
        existing = db.query(WishlistItem).filter(
            and_(WishlistItem.wishlist_id == wishlist.id, WishlistItem.product_id == product_id)
        ).first()

        if existing:
            raise ConflictException("Item already in wishlist")

        item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=product_id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info(f"Item added to wishlist: {product_id}")
        return item

    @staticmethod
    def remove_item(db: Session, item_id: str) -> None:
        """Remove item from wishlist."""
        item = db.query(WishlistItem).filter(WishlistItem.id == item_id).first()
        if not item:
            raise ResourceNotFoundException("WishlistItem", item_id)

        db.delete(item)
        db.commit()
        logger.info(f"Item removed from wishlist: {item_id}")

    @staticmethod
    def get_wishlist(db: Session, user_id: str) -> Wishlist:
        """Get user's wishlist."""
        wishlist = db.query(Wishlist).filter(Wishlist.user_id == user_id).first()
        if not wishlist:
            raise ResourceNotFoundException("Wishlist", user_id)
        return wishlist
