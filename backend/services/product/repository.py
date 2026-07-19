"""Product Service repository."""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .models import Product, Category, Review
from backend.shared.exceptions import ResourceNotFoundException, ConflictException
from backend.shared.utils import get_logger

logger = get_logger(__name__)


class CategoryRepository:
    """Repository for Category operations."""

    @staticmethod
    def create(
        db: Session,
        name: str,
        slug: str,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> Category:
        """Create a new category."""
        # Check if category exists
        existing = db.query(Category).filter(
            or_(Category.name == name, Category.slug == slug)
        ).first()
        
        if existing:
            raise ConflictException("Category already exists")

        category = Category(
            name=name,
            slug=slug,
            description=description,
            is_active=is_active,
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        logger.info(f"Category created: {category.id}")
        return category

    @staticmethod
    def get_by_id(db: Session, category_id: str) -> Category:
        """Get category by ID."""
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise ResourceNotFoundException("Category", category_id)
        return category

    @staticmethod
    def list_all(db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[Category], int]:
        """List all categories."""
        query = db.query(Category).filter(Category.is_active == True)
        total = query.count()
        categories = query.offset(skip).limit(limit).all()
        return categories, total


class ProductRepository:
    """Repository for Product operations."""

    @staticmethod
    def create(
        db: Session,
        name: str,
        sku: str,
        price: float,
        cost: float,
        category_id: str,
        stock: int = 0,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Product:
        """Create a new product."""
        # Verify category exists
        category = CategoryRepository.get_by_id(db, category_id)
        
        # Check if SKU exists
        existing = db.query(Product).filter(Product.sku == sku).first()
        if existing:
            raise ConflictException("Product with this SKU already exists")

        product = Product(
            name=name,
            sku=sku,
            price=price,
            cost=cost,
            category_id=category_id,
            stock=stock,
            description=description,
            image_url=image_url,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        logger.info(f"Product created: {product.id}")
        return product

    @staticmethod
    def get_by_id(db: Session, product_id: str) -> Product:
        """Get product by ID."""
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ResourceNotFoundException("Product", product_id)
        return product

    @staticmethod
    def search(
        db: Session,
        query: Optional[str] = None,
        category_id: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Product], int]:
        """Search products."""
        q = db.query(Product).filter(Product.is_active == True)

        if query:
            q = q.filter(
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                )
            )

        if category_id:
            q = q.filter(Product.category_id == category_id)

        if min_price is not None:
            q = q.filter(Product.price >= min_price)

        if max_price is not None:
            q = q.filter(Product.price <= max_price)

        if in_stock:
            q = q.filter(Product.stock > 0)

        total = q.count()
        products = q.offset(skip).limit(limit).all()
        return products, total

    @staticmethod
    def update(
        db: Session,
        product_id: str,
        **kwargs,
    ) -> Product:
        """Update product."""
        product = ProductRepository.get_by_id(db, product_id)
        
        for key, value in kwargs.items():
            if value is not None and hasattr(product, key):
                setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        logger.info(f"Product updated: {product_id}")
        return product


class ReviewRepository:
    """Repository for Review operations."""

    @staticmethod
    def create(
        db: Session,
        product_id: str,
        user_id: str,
        rating: int,
        title: str,
        comment: Optional[str] = None,
    ) -> Review:
        """Create a new review."""
        # Verify product exists
        product = ProductRepository.get_by_id(db, product_id)

        review = Review(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            title=title,
            comment=comment,
        )
        db.add(review)
        
        # Update product rating
        ProductRepository._update_product_rating(db, product_id)
        
        db.commit()
        db.refresh(review)
        logger.info(f"Review created: {review.id}")
        return review

    @staticmethod
    def get_by_id(db: Session, review_id: str) -> Review:
        """Get review by ID."""
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise ResourceNotFoundException("Review", review_id)
        return review

    @staticmethod
    def get_product_reviews(
        db: Session,
        product_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Review], int]:
        """Get reviews for a product."""
        q = db.query(Review).filter(Review.product_id == product_id)
        total = q.count()
        reviews = q.offset(skip).limit(limit).all()
        return reviews, total

    @staticmethod
    def _update_product_rating(db: Session, product_id: str) -> None:
        """Update product rating based on reviews."""
        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            product = db.query(Product).filter(Product.id == product_id).first()
            product.rating = round(avg_rating, 2)
            product.review_count = len(reviews)
