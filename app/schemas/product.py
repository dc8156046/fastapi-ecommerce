from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Create product schema
class ProductCreate(BaseModel):
    name: str
    slug: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    sku: str
    price: float
    stock: int
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None
    weight: Optional[float] = None
    discount_price: Optional[float] = None
    is_featured: Optional[bool] = False
    is_active: Optional[bool] = True
    brand_id: int


# Update product schema
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None
    weight: Optional[float] = None
    discount_price: Optional[float] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    brand_id: Optional[int] = None


# Product response schema
class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    sku: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    price: float
    stock: int
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None
    weight: Optional[float] = None
    discount_price: Optional[float] = None
    is_featured: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    brand_id: int

    class Config:
        from_attributes = True
