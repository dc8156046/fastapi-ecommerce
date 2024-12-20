from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid
from app.models.order import Order, OrderItem
from app.api.deps import get_current_active_user, get_db
from app.schemas.order import OrderCreate, OrderInDB, OrderUpdate

router = APIRouter()


def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


@router.post("/", response_model=OrderInDB)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    # Create new order
    db_order = Order(
        user_id=current_user.id,
        order_number=generate_order_number(),
        shipping_fee=order.shipping_fee,
        payment_method=order.payment_method,
        shipping_address_id=order.shipping_address_id,
        billing_address_id=order.billing_address_id,
    )
    db.add(db_order)

    # Add order items
    total_amount = 0
    for item in order.items:
        total_price = item.price * item.quantity
        total_amount += total_price

        db_item = OrderItem(
            order=db_order,
            product_id=item.product_id,
            product_name=item.product_name,
            product_sku=item.product_sku,
            quantity=item.quantity,
            price=item.price,
            total_price=total_price,
        )
        db.add(db_item)

    # Update order total
    db_order.total_amount = total_amount + order.shipping_fee

    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/", response_model=List[OrderInDB])
def get_orders(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    return (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{order_id}", response_model=OrderInDB)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order


@router.patch("/{order_id}", response_model=OrderInDB)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    db_order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Update order fields
    order_data = order_update.dict(exclude_unset=True)
    for field, value in order_data.items():
        setattr(db_order, field, value)

    db_order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    db_order = (
        db.query(Order)
        .filter(Order.id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not db_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Soft delete
    db_order.is_active = False
    db_order.updated_at = datetime.utcnow()
    db.commit()
