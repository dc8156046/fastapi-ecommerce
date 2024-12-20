from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api.deps import get_current_active_superuser, get_db
from app.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductList,
)
from app.models.category import Category
from app.models.brand import Brand

router = APIRouter()


@router.get(
    "/",
    response_model=ProductList,
    summary="Get products list",
    status_code=status.HTTP_200_OK,
)
async def get_products(
    skip: int = 0,
    limit: int = 15,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    query = db.query(Product)

    # Apply filters
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    total = query.count()
    products = query.offset(skip).limit(limit).all()

    return {
        "message": "Get products list successfully",
        "data": products,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product detail",
    status_code=status.HTTP_200_OK,
)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    return {"message": "Get product detail successfully", "data": product}


@router.post(
    "/",
    response_model=ProductResponse,
    summary="Create product",
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_create: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Validate category
    if product_create.category_id:
        category = (
            db.query(Category).filter(Category.id == product_create.category_id).first()
        )
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {product_create.category_id} not found",
            )

    # Validate brand
    if product_create.brand_id:
        brand = db.query(Brand).filter(Brand.id == product_create.brand_id).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {product_create.brand_id} not found",
            )

    # Check if product with same SKU exists
    if db.query(Product).filter(Product.sku == product_create.sku).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists",
        )

    try:
        # Create product
        product_data = product_create.model_dump(exclude={"variants", "attributes"})
        db_product = Product(**product_data)
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Create variants if provided
        if product_create.variants:
            for variant in product_create.variants:
                variant_data = variant.model_dump()
                variant_data["product_id"] = db_product.id
                db_variant = ProductVariant(**variant_data)
                db.add(db_variant)

        # Create attributes if provided
        if product_create.attributes:
            for attr in product_create.attributes:
                attr_data = attr.model_dump()
                attr_data["product_id"] = db_product.id
                db_attr = ProductAttribute(**attr_data)
                db.add(db_attr)

        db.commit()
        db.refresh(db_product)

        return {"message": "Create product successfully", "data": db_product}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if product exists
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    try:
        # Validate category if provided
        if product_update.category_id:
            category = (
                db.query(Category)
                .filter(Category.id == product_update.category_id)
                .first()
            )
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID {product_update.category_id} not found",
                )

        # Validate brand if provided
        if product_update.brand_id:
            brand = db.query(Brand).filter(Brand.id == product_update.brand_id).first()
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Brand with ID {product_update.brand_id} not found",
                )

        # Check SKU uniqueness if being updated
        if product_update.sku and product_update.sku != db_product.sku:
            if db.query(Product).filter(Product.sku == product_update.sku).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this SKU already exists",
                )

        # Update product fields
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)

        return {"message": "Update product successfully", "data": db_product}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{product_id}",
    response_model=dict,
    summary="Delete product",
    status_code=status.HTTP_200_OK,  # Changed from 204 to 200 to allow response body
)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if product exists
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )

    try:
        # Set deleted_at timestamp instead of actual deletion
        db_product.deleted_at = datetime.utcnow()
        db_product.is_active = False
        db.commit()

        return {"message": "Delete product successfully", "data": {"id": product_id}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
