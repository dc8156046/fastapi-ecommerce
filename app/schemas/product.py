from pydantic import BaseModel, Field, HttpUrl, constr, validator
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class BaseSchema(BaseModel):
    """Base schema for all schemas"""

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat(), Decimal: lambda v: str(v)}


# Product response schema
class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    sku: str
    price: float
    stock: int
    brand_id: int
    short_description: Optional[str] = None
    description: Optional[str] = None
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

    class Config:
        from_attributes = True


# Product attribute base schema
class ProductAttributeBase(BaseSchema):
    """Product attribute base schema"""

    name: str = Field(..., min_length=1, max_length=100, description="Attribute name")
    value: str = Field(..., min_length=1, max_length=255, description="Attribute value")
    description: Optional[str] = Field(
        None, max_length=500, description="Attribute description"
    )
    attribute_type: str = Field("text", description="Attribute type")
    is_active: bool = Field(True, description="Is attribute active")
    sort_order: int = Field(0, description="Sort order")


class ProductAttributeCreate(ProductAttributeBase):
    """Create product attribute schema"""

    product_id: int = Field(..., gt=0, description="Related product ID")


class ProductAttribute(ProductAttributeBase):
    """Product attribute schema"""

    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime


# Product image base schema
class ProductImageBase(BaseSchema):
    """Product image base schema"""

    image_url: HttpUrl = Field(..., max_length=255, description="Image URL")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text")
    main_image: bool = Field(False, description="Is main image")
    is_active: bool = Field(True, description="Is image active")
    sort_order: int = Field(0, description="Sort order")
    width: Optional[int] = Field(None, gt=0, description="Image width")
    height: Optional[int] = Field(None, gt=0, description="Image height")
    image_size: Optional[int] = Field(None, gt=0, description="Image size in bytes")


class ProductImageCreate(ProductImageBase):
    """Create product image schema"""

    product_id: int = Field(..., gt=0, description="Related product ID")


class ProductImage(ProductImageBase):
    """Product image schema"""

    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime


# Product variant attribute base schema
class ProductVariantAttributeBase(BaseSchema):
    """Product variant attribute base schema"""

    variant_id: int = Field(..., gt=0, description="Related variant ID")
    attribute_id: int = Field(..., gt=0, description="Related attribute ID")


class ProductVariantAttribute(ProductVariantAttributeBase):
    """Product variant attribute schema"""

    id: int
    created_at: datetime
    updated_at: datetime


class ProductVariantBase(BaseSchema):
    """Product variant base schema"""

    name: str = Field(..., min_length=1, max_length=100, description="Variant name")
    sku: constr(min_length=1, max_length=100) = Field(..., description="Variant SKU")
    price: Decimal = Field(..., gt=0, description="Variant price")
    stock: int = Field(0, ge=0, description="Variant stock")
    barcode: Optional[str] = Field(None, max_length=100, description="Variant barcode")
    currency: str = Field("USD", min_length=3, max_length=3, description="Currency")
    weight: Optional[Decimal] = Field(None, gt=0, description="Weight (kg)")
    is_active: bool = Field(True, description="Is variant active")

    @validator("currency")
    def validate_currency(cls, v):
        """Validate currency code"""
        if v.upper() != v:
            raise ValueError("Currency code must be uppercase")
        return v


class ProductVariantCreate(ProductVariantBase):
    """Create product variant schema"""

    product_id: int = Field(..., gt=0, description="Related product ID")
    attributes: Optional[List[int]] = Field(None, description="Related attribute IDs")


class ProductVariant(ProductVariantBase):
    """Product variant schema"""

    id: int
    product_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    attributes: List[ProductVariantAttribute] = []


# Product base schema
class ProductBase(BaseSchema):
    """Product base schema"""

    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    slug: constr(min_length=1, max_length=100) = Field(
        ..., description="Product slug (URL)"
    )
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    short_description: Optional[str] = Field(
        None, max_length=255, description="Short description"
    )
    seo_title: Optional[str] = Field(None, max_length=100, description="SEO title")
    seo_description: Optional[str] = Field(
        None, max_length=255, description="SEO description"
    )
    seo_keywords: Optional[str] = Field(
        None, max_length=255, description="SEO keywords"
    )
    sku: constr(min_length=1, max_length=100) = Field(..., description="SKU")
    price: Decimal = Field(..., gt=0, description="Price")
    stock: int = Field(0, ge=0, description="Stock")
    weight: Optional[Decimal] = Field(None, gt=0, description="Weight (kg)")
    width: Optional[Decimal] = Field(None, gt=0, description="Width (cm)")
    height: Optional[Decimal] = Field(None, gt=0, description="Height (cm)")
    depth: Optional[Decimal] = Field(None, gt=0, description="Depth (cm)")
    discount_price: Optional[Decimal] = Field(None, gt=0, description="Discount price")
    currency: str = Field("USD", min_length=3, max_length=3, description="Currency")
    is_featured: bool = Field(False, description="Is featured")
    is_active: bool = Field(True, description="Is active")

    @validator("slug")
    def validate_slug(cls, v):
        """Validate slug"""
        if not v.islower() or not v.replace("-", "").isalnum():
            raise ValueError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        return v

    @validator("discount_price")
    def validate_discount_price(cls, v, values):
        """Validate discount price"""
        if v is not None and "price" in values and v >= values["price"]:
            raise ValueError("Discount price must be lower than regular price")
        return v


class ProductCreate(ProductBase):
    """Create product schema"""

    category_id: int = Field(..., gt=0, description="Category ID")
    brand_id: int = Field(..., gt=0, description="Brand ID")


class ProductUpdate(BaseSchema):
    """Update product schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    discount_price: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    weight: Optional[Decimal] = Field(None, gt=0)
    width: Optional[Decimal] = Field(None, gt=0)
    height: Optional[Decimal] = Field(None, gt=0)
    depth: Optional[Decimal] = Field(None, gt=0)
    seo_title: Optional[str] = Field(None, max_length=100)
    seo_description: Optional[str] = Field(None, max_length=255)
    seo_keywords: Optional[str] = Field(None, max_length=255)

    # ... 其他可选字段


class Product(ProductBase):
    """Product schema"""

    id: int
    category_id: int
    brand_id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    images: List[ProductImage] = []
    attributes: List[ProductAttribute] = []
    variants: List[ProductVariant] = []


class ProductList(BaseSchema):
    """Product list schema"""

    id: int
    name: str
    slug: str
    price: Decimal
    stock: int
    is_active: bool
    main_image: Optional[str] = None

    @validator("main_image", pre=True)
    def get_main_image(cls, v, values):
        """Get main image URL"""
        if isinstance(v, list) and v:
            return next((img.image_url for img in v if img.main_image), None)
        return None
