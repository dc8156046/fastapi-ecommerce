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


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: List["CategoryResponse"] = []

    class Config:
        from_attributes = True


# This is needed for the self-referencing type hint to work
CategoryResponse.model_rebuild()
