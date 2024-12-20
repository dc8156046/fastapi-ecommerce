from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.api.deps import get_current_active_superuser, get_db
from app.schemas.product import (
    ProductAttribute,
    ProductAttributeCreate,
    ProductAttributeUpdate,
    ProductVariant,
    ProductVariantCreate,
    ProductVariantUpdate,
)
from app.models.product import ProductAttribute as ProductAttributeModel
from app.models.product import ProductVariant as ProductVariantModel
from app.models.product import ProductVariantAttribute as ProductVariantAttributeModel

router = APIRouter()


# Product Attribute Routes
@router.post(
    "/attributes/", response_model=ProductAttribute, status_code=status.HTTP_201_CREATED
)
def create_product_attribute(
    attribute: ProductAttributeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db_attribute = ProductAttributeModel(**attribute.model_dump())
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute


@router.get("/attributes/", response_model=List[ProductAttribute])
def list_product_attributes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    attributes = db.query(ProductAttributeModel).offset(skip).limit(limit).all()
    return attributes


@router.get("/attributes/{attribute_id}", response_model=ProductAttribute)
def get_product_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    attribute = (
        db.query(ProductAttributeModel)
        .filter(ProductAttributeModel.id == attribute_id)
        .first()
    )
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return attribute


@router.put("/attributes/{attribute_id}", response_model=ProductAttribute)
def update_product_attribute(
    attribute_id: int,
    attribute: ProductAttributeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db_attribute = (
        db.query(ProductAttributeModel)
        .filter(ProductAttributeModel.id == attribute_id)
        .first()
    )
    if not db_attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    for key, value in attribute.model_dump(exclude_unset=True).items():
        setattr(db_attribute, key, value)

    db.commit()
    db.refresh(db_attribute)
    return db_attribute


@router.delete("/attributes/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_attribute(
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db_attribute = (
        db.query(ProductAttributeModel)
        .filter(ProductAttributeModel.id == attribute_id)
        .first()
    )
    if not db_attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    db.delete(db_attribute)
    db.commit()
    return None


# Product Variant Routes
@router.post(
    "/variants/", response_model=ProductVariant, status_code=status.HTTP_201_CREATED
)
def create_product_variant(
    variant: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Create variant
    variant_data = variant.model_dump(exclude={"attributes"})
    db_variant = ProductVariantModel(**variant_data)
    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)

    # Create variant attributes
    for attr in variant.attributes:
        db_variant_attr = ProductVariantAttributeModel(
            variant_id=db_variant.id, attribute_id=attr.attribute_id
        )
        db.add(db_variant_attr)

    db.commit()
    db.refresh(db_variant)
    return db_variant


@router.get("/variants/", response_model=List[ProductVariant])
def list_product_variants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    variants = (
        db.query(ProductVariantModel)
        .filter(ProductVariantModel.deleted_at.is_(None))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return variants


@router.get("/variants/{variant_id}", response_model=ProductVariant)
def get_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    variant = (
        db.query(ProductVariantModel)
        .filter(
            ProductVariantModel.id == variant_id,
            ProductVariantModel.deleted_at.is_(None),
        )
        .first()
    )
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    return variant


@router.put("/variants/{variant_id}", response_model=ProductVariant)
def update_product_variant(
    variant_id: int,
    variant: ProductVariantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db_variant = (
        db.query(ProductVariantModel)
        .filter(
            ProductVariantModel.id == variant_id,
            ProductVariantModel.deleted_at.is_(None),
        )
        .first()
    )
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Update variant fields
    variant_data = variant.model_dump(exclude={"attributes"}, exclude_unset=True)
    for key, value in variant_data.items():
        setattr(db_variant, key, value)

    # Update variant attributes if provided
    if variant.attributes is not None:
        # Remove existing attributes
        db.query(ProductVariantAttributeModel).filter(
            ProductVariantAttributeModel.variant_id == variant_id
        ).delete()

        # Add new attributes
        for attr in variant.attributes:
            db_variant_attr = ProductVariantAttributeModel(
                variant_id=variant_id, attribute_id=attr.attribute_id
            )
            db.add(db_variant_attr)

    db.commit()
    db.refresh(db_variant)
    return db_variant


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db_variant = (
        db.query(ProductVariantModel)
        .filter(
            ProductVariantModel.id == variant_id,
            ProductVariantModel.deleted_at.is_(None),
        )
        .first()
    )
    if not db_variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    # Soft delete
    db_variant.deleted_at = datetime.utcnow()
    db.commit()
    return None
