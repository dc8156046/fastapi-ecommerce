from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Date,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


# Category model
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(255), nullable=True)
    seo_title = Column(String(100), nullable=True)
    seo_description = Column(String(255), nullable=True)
    seo_keywords = Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    parent = relationship("Category", remote_side=[id])
    children = relationship("Category")
    products = relationship("Product", back_populates="category")
    subcategories = relationship("Category", back_populates="parent")
