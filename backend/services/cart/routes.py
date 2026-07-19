"""Cart Service API routes."""

from fastapi import APIRouter, Depends, status, HTTPException, Path
from sqlalchemy.orm import Session

from .schemas import (
    CartResponse,
    CartItemResponse,
    AddToCartRequest,
    UpdateCartItemRequest,
    WishlistResponse,
    WishlistItemResponse,
)
from .service import CartService, WishlistService
from backend.shared.deps import get_db, require_user
from backend.shared.security import TokenData
from backend.shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/cart", tags=["cart"])


@router.get(
    "",
    response_model=CartResponse,
    summary="Get user's cart",
    description="Get authenticated user's shopping cart",
)
async def get_cart(
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get user's cart."""
    try:
        cart = CartService.get_cart(db, current_user.user_id)
        return CartResponse.from_attributes(cart)
    except Exception as e:
        logger.error(f"Error fetching cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cart",
        )


@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Add item to cart",
    description="Add product to user's shopping cart",
)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Add item to cart."""
    try:
        cart = CartService.add_to_cart(
            db=db,
            user_id=current_user.user_id,
            product_id=request.product_id,
            quantity=request.quantity,
            price=request.price,
        )
        return CartResponse.from_attributes(cart)
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart",
        )


@router.put(
    "/items/{item_id}",
    response_model=CartResponse,
    summary="Update cart item",
    description="Update quantity of item in cart",
)
async def update_cart_item(
    item_id: str = Path(...),
    request: UpdateCartItemRequest = None,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Update cart item quantity."""
    try:
        CartService.update_cart_item(db, item_id, request.quantity)
        cart = CartService.get_cart(db, current_user.user_id)
        return CartResponse.from_attributes(cart)
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item",
        )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from cart",
    description="Remove product from user's shopping cart",
)
async def remove_from_cart(
    item_id: str = Path(...),
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Remove item from cart."""
    try:
        CartService.remove_from_cart(db, item_id)
        return None
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from cart",
        )


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear cart",
    description="Remove all items from user's shopping cart",
)
async def clear_cart(
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Clear user's cart."""
    try:
        CartService.clear_cart(db, current_user.user_id)
        return None
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart",
        )


# Wishlist routes
wishlist_router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@wishlist_router.get(
    "",
    response_model=WishlistResponse,
    summary="Get user's wishlist",
    description="Get authenticated user's wishlist",
)
async def get_wishlist(
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Get user's wishlist."""
    try:
        wishlist = WishlistService.get_wishlist(db, current_user.user_id)
        return WishlistResponse.from_attributes(wishlist)
    except Exception as e:
        logger.error(f"Error fetching wishlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch wishlist",
        )


@wishlist_router.post(
    "/items",
    response_model=WishlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to wishlist",
    description="Add product to user's wishlist",
)
async def add_to_wishlist(
    request: dict,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Add item to wishlist."""
    try:
        wishlist = WishlistService.add_to_wishlist(
            db=db,
            user_id=current_user.user_id,
            product_id=request["product_id"],
        )
        return WishlistResponse.from_attributes(wishlist)
    except Exception as e:
        logger.error(f"Error adding to wishlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to wishlist",
        )


@wishlist_router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from wishlist",
    description="Remove product from user's wishlist",
)
async def remove_from_wishlist(
    item_id: str = Path(...),
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Remove item from wishlist."""
    try:
        WishlistService.remove_from_wishlist(db, item_id)
        return None
    except Exception as e:
        logger.error(f"Error removing from wishlist: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from wishlist",
        )
