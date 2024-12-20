from pydantic import BaseModel, Field, constr
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Attribute name")
    slug: constr(min_length=1, max_length=100) = Field(
        ..., description="Category slug (URL)"
    )
    description: Optional[str] = None
    is_active: Optional[bool] = True
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: List["CategoryResponse"] = []

    class Config:
        from_attributes = True


# This is needed for the self-referencing type hint to work
CategoryResponse.model_rebuild()


class ProductInCategory(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    price: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryInDB(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: List["CategoryInDB"] = []
    products: List[ProductInCategory] = []

    class Config:
        from_attributes = True


# This is needed for the self-referential relationship
CategoryInDB.update_forward_refs()


class PaginatedProductResponse(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    items: List[ProductInCategory]

    class Config:
        from_attributes = True
