from pydantic import BaseModel, Field, constr
from typing import Optional
from datetime import datetime


# Brand base schema
class BrandBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="brand name")
    slug: constr(min_length=1, max_length=100) = Field(
        ..., description="Brand slug (URL)"
    )
    logo_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None
    is_active: Optional[bool] = True


# Brand create schema
class BrandCreate(BrandBase):
    pass


# Brand update schema
class BrandUpdate(BrandBase):
    pass


# Brand response schema
class BrandResponse(BrandBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
