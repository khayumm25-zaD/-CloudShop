"""Product Service schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CategoryBase(BaseModel):
    """Category base schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    slug: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    """Create category schema."""
    pass


class CategoryResponse(CategoryBase):
    """Category response schema."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Product base schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=50)
    price: Decimal = Field(..., decimal_places=2, ge=0)
    cost: Decimal = Field(..., decimal_places=2, ge=0)
    category_id: str
    stock: int = Field(0, ge=0)
    is_active: bool = True
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    """Create product schema."""
    pass


class ProductUpdate(BaseModel):
    """Update product schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    image_url: Optional[str] = None


class ProductResponse(ProductBase):
    """Product response schema."""

    id: str
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewBase(BaseModel):
    """Review base schema."""

    rating: int = Field(..., ge=1, le=5)
    title: str = Field(..., min_length=1, max_length=255)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Create review schema."""
    product_id: str


class ReviewResponse(ReviewBase):
    """Review response schema."""

    id: str
    product_id: str
    user_id: str
    is_verified: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    """Product detail with reviews."""

    reviews: List[ReviewResponse] = []


class SearchProductRequest(BaseModel):
    """Search products request."""

    query: Optional[str] = None
    category_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
