"""Product Service business logic."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from .repository import ProductRepository, CategoryRepository, ReviewRepository
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class ProductService:
    """Business logic for products."""

    @staticmethod
    def search_products(
        db: Session,
        query: Optional[str] = None,
        category_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ):
        """Search products with filters."""
        skip = (page - 1) * page_size
        products, total = ProductRepository.search(
            db=db,
            query=query,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
            skip=skip,
            limit=page_size,
        )
        
        total_pages = (total + page_size - 1) // page_size
        return {
            "products": products,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        }

    @staticmethod
    def get_product_details(db: Session, product_id: str):
        """Get product with reviews."""
        product = ProductRepository.get_by_id(db, product_id)
        reviews, _ = ReviewRepository.get_product_reviews(db, product_id, limit=10)
        return {
            "product": product,
            "reviews": reviews,
        }

    @staticmethod
    def add_review(
        db: Session,
        product_id: str,
        user_id: str,
        rating: int,
        title: str,
        comment: Optional[str] = None,
    ):
        """Add review to product."""
        review = ReviewRepository.create(
            db=db,
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            title=title,
            comment=comment,
        )
        logger.info(f"Review added for product: {product_id}")
        return review
