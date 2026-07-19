"""Product Service - Product catalog, categories, and reviews."""

from sqlalchemy import Column, String, Float, Integer, Boolean, Text, ForeignKey, Index, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.shared.models import BaseModel


class Category(BaseModel):
    """Product category model."""

    __tablename__ = "categories"
    __table_args__ = (
        Index("idx_name", "name", unique=True),
    )

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"


class Product(BaseModel):
    """Product model."""

    __tablename__ = "products"
    __table_args__ = (
        Index("idx_category_id", "category_id"),
        Index("idx_name", "name"),
        Index("idx_sku", "sku", unique=True),
    )

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(50), nullable=False, unique=True, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    image_url = Column(String(500), nullable=True)
    created_at = Column(datetime, default=datetime.utcnow, nullable=False)
    updated_at = Column(datetime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category = relationship("Category", back_populates="products")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"


class Review(BaseModel):
    """Product review model."""

    __tablename__ = "reviews"
    __table_args__ = (
        Index("idx_product_id", "product_id"),
        Index("idx_user_id", "user_id"),
    )

    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    user_id = Column(String(36), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5
    title = Column(String(255), nullable=False)
    comment = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(datetime, default=datetime.utcnow, nullable=False)
    updated_at = Column(datetime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review {self.title}>"
