from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Enums
class OrderStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class PaymentStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"


class PaymentMethod(str, Enum):
    CREDIT_CARD = "Credit Card"
    PAYPAL = "PayPal"
    BANK_TRANSFER = "Bank Transfer"


# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    price: Decimal
    product_name: str
    product_sku: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = None
    product_name: Optional[str] = None
    product_sku: Optional[str] = None


class OrderItemInDB(OrderItemBase):
    id: int
    order_id: int
    total_price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Order Schemas
class OrderBase(BaseModel):
    shipping_fee: Optional[Decimal] = Field(default=0.0, ge=0)
    payment_method: Optional[PaymentMethod] = None
    shipping_address_id: int
    billing_address_id: int


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

    @validator("items")
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order must have at least one item")
        return v


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    shipping_fee: Optional[Decimal] = Field(None, ge=0)
    shipping_address_id: Optional[int] = None
    billing_address_id: Optional[int] = None
    is_active: Optional[bool] = None


class OrderInDB(OrderBase):
    id: int
    user_id: int
    order_number: str
    total_amount: Decimal
    status: OrderStatus
    payment_status: PaymentStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemInDB]

    class Config:
        from_attributes = True
