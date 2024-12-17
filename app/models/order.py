from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Enum,
    DECIMAL,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
import enum


# Define enums for status and payment method
class OrderStatus(enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class PaymentStatus(enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"


class PaymentMethod(enum.Enum):
    CREDIT_CARD = "Credit Card"
    PAYPAL = "PayPal"
    BANK_TRANSFER = "Bank Transfer"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_number = Column(String(100), unique=True, index=True)
    total_amount = Column(DECIMAL, nullable=False)
    shipping_fee = Column(DECIMAL, nullable=True, default=0.0)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = Column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False
    )
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"))
    billing_address_id = Column(Integer, ForeignKey("addresses.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="orders")
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(100), nullable=False)
    product_sku = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(DECIMAL, nullable=False)
    total_price = Column(DECIMAL, nullable=False)  # quantity * price
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
