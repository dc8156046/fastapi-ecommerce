from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Date,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    slug = Column(String(100), index=True)
    description = Column(String(255), nullable=True)
    short_description = Column(String(100), nullable=True)
    seo_title = Column(String(100), nullable=True)
    seo_description = Column(String(255), nullable=True)
    seo_keywords = Column(String(255), nullable=True)
    sku = Column(String(100), unique=True, index=True)
    price = Column(DECIMAL, index=True)
    stock = Column(Integer, index=True)
    weight = Column(DECIMAL, nullable=True)
    width = Column(DECIMAL, nullable=True)
    height = Column(DECIMAL, nullable=True)
    depth = Column(DECIMAL, nullable=True)
    discount_price = Column(DECIMAL, nullable=True)
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category_id = Column(Integer, ForeignKey("categories.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"))

    category = relationship("Category", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    images = relationship("ProductImage", back_populates="product")
    attributes = relationship("ProductAttribute", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    image_url = Column(String(255), index=True)
    alt_text = Column(String(255), nullable=True)
    main_image = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="images")


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    name = Column(String(100), index=True)
    value = Column(String(100), index=True)
    attribute_type = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="attributes")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    name = Column(String(100), index=True)
    sku = Column(String(100), unique=True, index=True)
    price = Column(DECIMAL, index=True)
    stock = Column(Integer, index=True)
    barcode = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="variants")
    attributes = relationship("ProductVariantAttribute", back_populates="variant")


class ProductVariantAttribute(Base):
    __tablename__ = "product_variant_attributes"

    id = Column(Integer, primary_key=True, index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"))
    attribute_id = Column(Integer, ForeignKey("product_attributes.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    variant = relationship("ProductVariant", back_populates="attributes")
    attribute = relationship("ProductAttribute")


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
