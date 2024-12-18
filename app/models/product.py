from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Date,
    DECIMAL,
    Enum as SQLEnum,  # Rename Enum to SQLEnum
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
from enum import Enum


class AttributeType(str, Enum):
    """Product attribute type enumeration

    Define the type of product attribute, such as text, number, color, etc.
    - TEXT: Text type, such as color, size, etc.
    - NUMBER: Number type, such as weight, height, etc.
    - COLOR: Color type, such as red, blue, etc.
    - SIZE: Size type, such as S, M, L, etc.
    - BOOLEAN: Boolean type, such as true or false.
    """

    TEXT = "text"
    NUMBER = "number"
    COLOR = "color"
    SIZE = "size"
    BOOLEAN = "boolean"


class Product(Base):
    """Product model

    Store product information, including name, description, price, stock, etc.
    """

    __tablename__ = "products"

    # Basic information
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False, comment="product name")
    slug = Column(
        String(100),
        index=True,
        unique=True,
        nullable=False,
        comment="URL slug for SEO",
    )
    description = Column(String(1000), nullable=True, comment="product description")
    short_description = Column(String(255), nullable=True, comment="short description")

    # SEO information
    seo_title = Column(String(100), nullable=True, comment="SEO title")
    seo_description = Column(String(255), nullable=True, comment="SEO description")
    seo_keywords = Column(String(255), nullable=True, comment="SEO keywords")

    # product information
    sku = Column(
        String(100), unique=True, index=True, nullable=False, comment="SKU code"
    )
    price = Column(DECIMAL(10, 2), index=True, nullable=False, comment="selling price")
    stock = Column(Integer, index=True, default=0, comment="stock quantity")

    # Size and weight
    weight = Column(DECIMAL(10, 2), nullable=True, comment="Weight(kg)")
    width = Column(DECIMAL(10, 2), nullable=True, comment="Width(cm)")
    height = Column(DECIMAL(10, 2), nullable=True, comment="Height(cm)")
    depth = Column(DECIMAL(10, 2), nullable=True, comment="Depth(cm)")

    # Discount and promotion
    discount_price = Column(DECIMAL(10, 2), nullable=True, comment="discount price")
    currency = Column(String(3), default="USD", nullable=False, comment="currency")
    is_featured = Column(Boolean, default=False, comment="whether it is featured")
    is_active = Column(Boolean, default=True, comment="whether it is active")

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="creation time"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="update time",
    )
    deleted_at = Column(DateTime, nullable=True, comment="deletion time (soft delete)")

    # Foreign keys
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=False, comment="category ID"
    )
    brand_id = Column(
        Integer, ForeignKey("brands.id"), nullable=False, comment="brand ID"
    )

    # Relationships
    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    images = relationship(
        "ProductImage", back_populates="product", cascade="all, delete-orphan"
    )
    attributes = relationship(
        "ProductAttribute", back_populates="product", cascade="all, delete-orphan"
    )
    variants = relationship(
        "ProductVariant", back_populates="product", cascade="all, delete-orphan"
    )


class ProductImage(Base):
    """Product image model

    Store product image information, including image URL, alt text, etc.
    """

    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer, ForeignKey("products.id"), nullable=False, comment="related product ID"
    )
    image_url = Column(String(255), index=True, nullable=False, comment="image URL")
    alt_text = Column(String(255), nullable=True, comment="Image alt text")
    main_image = Column(Boolean, default=False, comment="whether it is the main image")
    is_active = Column(Boolean, default=True, comment="whether it is active")
    sort_order = Column(Integer, default=0, comment="sort order")

    # Image metadata
    image_size = Column(Integer, nullable=True, comment="image size (bytes)")
    width = Column(Integer, nullable=True, comment="image width (pixels)")
    height = Column(Integer, nullable=True, comment="image height (pixels)")

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="creation time"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="update time",
    )

    # Relationships
    product = relationship("Product", back_populates="images")


class ProductAttribute(Base):
    """Product attribute model

    Store product attribute information, such as color, size, etc.
    Each attribute can be referenced by product variants to define specific product specifications.
    """

    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer, ForeignKey("products.id"), nullable=False, comment="related product ID"
    )
    name = Column(
        String(100), index=True, nullable=False, comment="attribute name"
    )  # such as color, size, etc.
    value = Column(
        String(255), index=True, nullable=False, comment="attribute value"
    )  # such as red, blue, etc.
    description = Column(String(500), nullable=True, comment="attribute description")
    attribute_type = Column(
        SQLEnum(AttributeType),
        nullable=False,
        default=AttributeType.TEXT,
        comment="attribute type",
    )
    is_active = Column(Boolean, default=True, comment="whether it is active")
    sort_order = Column(Integer, default=0, comment="sort order")

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="creation time"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="update time",
    )

    # Relationships
    product = relationship("Product", back_populates="attributes")
    variant_attributes = relationship(
        "ProductVariantAttribute", back_populates="attribute"
    )


class ProductVariant(Base):
    """Product variant model

    Store product variant information, such as price, stock, etc.
    Each variant can be referenced by a product to define different product options.
    """

    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(
        Integer, ForeignKey("products.id"), nullable=False, comment="related product ID"
    )
    name = Column(
        String(100), index=True, nullable=False, comment="variant name"
    )  # such as red, blue, etc.
    sku = Column(
        String(100), unique=True, index=True, nullable=False, comment="variant SKU code"
    )
    price = Column(DECIMAL(10, 2), index=True, nullable=False, comment="variant price")
    stock = Column(Integer, index=True, default=0, comment="variant stock quantity")
    barcode = Column(String(100), nullable=True, comment="variant barcode")
    currency = Column(String(3), default="USD", nullable=False, comment="currency")
    weight = Column(DECIMAL(10, 2), nullable=True, comment="variant weight(kg)")
    is_active = Column(Boolean, default=True, comment="whether it is active")

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="creation time"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="update time",
    )
    deleted_at = Column(DateTime, nullable=True, comment="deletion time (soft delete)")

    # Relationships
    product = relationship("Product", back_populates="variants")
    attributes = relationship(
        "ProductVariantAttribute",
        back_populates="variant",
        cascade="all, delete-orphan",
    )


class ProductVariantAttribute(Base):
    """Product variant attribute model

    Store the specific attribute combination for each variant.
    """

    __tablename__ = "product_variant_attributes"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(
        Integer,
        ForeignKey("product_variants.id"),
        nullable=False,
        comment="related variant ID",
    )
    attribute_id = Column(
        Integer,
        ForeignKey("product_attributes.id"),
        nullable=False,
        comment="related attribute ID",
    )

    # Timestamps
    created_at = Column(
        DateTime, default=datetime.utcnow, nullable=False, comment="creation time"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="update time",
    )

    # Relationships
    variant = relationship("ProductVariant", back_populates="attributes")
    attribute = relationship("ProductAttribute", back_populates="variant_attributes")


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=True)
    rating = Column(Integer, index=True)
    review = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    helpful_votes = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
