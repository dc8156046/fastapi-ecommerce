from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_active_superuser, get_db
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse

router = APIRouter()


@router.get(
    "/",
    response_model=dict,
    summary="Get brands list",
    status_code=status.HTTP_200_OK,
)
async def get_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    brands = db.query(Brand).offset(skip).limit(limit).all()
    total = db.query(Brand).count()

    return {
        "message": "Get brands list successfully",
        "data": brands,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/{brand_id}",
    response_model=dict,
    summary="Get brand detail",
    status_code=status.HTTP_200_OK,
)
async def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with ID {brand_id} not found",
        )

    return {"message": "Get brand detail successfully", "data": brand}


@router.post(
    "/",
    response_model=dict,
    summary="Create brand",
    status_code=status.HTTP_201_CREATED,
)
async def create_brand(
    brand_create: BrandCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if brand with same name exists
    if db.query(Brand).filter(Brand.name == brand_create.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand with this name already exists",
        )

    try:
        # Create new brand
        brand_data = brand_create.model_dump()
        db_brand = Brand(**brand_data)
        db.add(db_brand)
        db.commit()
        db.refresh(db_brand)

        return {"message": "Create brand successfully", "data": db_brand}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{brand_id}",
    response_model=dict,
    summary="Update brand",
    status_code=status.HTTP_200_OK,
)
async def update_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if brand exists
    db_brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with ID {brand_id} not found",
        )

    try:
        # Check name uniqueness if name is being updated
        if brand_update.name and brand_update.name != db_brand.name:
            if db.query(Brand).filter(Brand.name == brand_update.name).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Brand with this name already exists",
                )

        # Update brand
        update_data = brand_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_brand, key, value)

        db.commit()
        db.refresh(db_brand)

        return {"message": "Update brand successfully", "data": db_brand}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{brand_id}",
    response_model=dict,
    summary="Delete brand",
    status_code=status.HTTP_200_OK,  # Changed from 204 to 200 to allow response body
)
async def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if brand exists
    db_brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not db_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with ID {brand_id} not found",
        )

    try:
        db.delete(db_brand)
        db.commit()
        return {"message": "Delete brand successfully", "data": {"id": brand_id}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
