"""Product Service API routes."""

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from .schemas import (
    ProductResponse,
    ProductDetailResponse,
    CategoryResponse,
    ReviewResponse,
    ReviewCreate,
    SearchProductRequest,
)
from .service import ProductService
from .repository import ProductRepository, CategoryRepository, ReviewRepository
from backend.shared.deps import get_db, require_user
from backend.shared.security import TokenData
from backend.shared.utils import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/products", tags=["products"])


@router.get(
    "/search",
    response_model=dict,
    summary="Search products",
    description="Search products with filters",
)
async def search_products(
    query: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[str] = Query(None, description="Category ID"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="In stock filter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search products with filters."""
    result = ProductService.search_products(
        db=db,
        query=query,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        page=page,
        page_size=page_size,
    )
    return result


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Get product details",
    description="Get product with reviews",
)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
):
    """Get product details."""
    try:
        result = ProductService.get_product_details(db, product_id)
        return {
            **result["product"].to_dict(),
            "reviews": [r.to_dict() for r in result["reviews"]],
        }
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch product",
        )


@router.post(
    "/{product_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add product review",
    description="Add a review to a product",
)
async def add_review(
    product_id: str,
    review: ReviewCreate,
    current_user: TokenData = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Add review to product."""
    try:
        new_review = ProductService.add_review(
            db=db,
            product_id=product_id,
            user_id=current_user.user_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
        )
        return ReviewResponse.from_attributes(new_review)
    except Exception as e:
        logger.error(f"Error adding review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add review",
        )


@router.get(
    "/categories",
    response_model=list,
    summary="Get all categories",
    description="Get list of product categories",
)
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get all categories."""
    categories, total = CategoryRepository.list_all(db, skip=skip, limit=limit)
    return {
        "categories": [CategoryResponse.from_attributes(c) for c in categories],
        "total": total,
    }


@router.get(
    "/health",
    summary="Health check",
    description="Check if product service is healthy",
)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint."""
    try:
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "product",
            "version": "1.0.0",
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable",
        )
