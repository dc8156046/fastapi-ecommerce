from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Create product schema
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    is_active: Optional[bool] = True
    brand_id: int


# Update product schema
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    brand_id: Optional[int] = None


# Product response schema
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    brand_id: int

    class Config:
        from_attributes = True
