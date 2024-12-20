from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_active_superuser, get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.get(
    "/",
    response_model=dict,
    summary="Get categories list",
    status_code=status.HTTP_200_OK,
)
async def get_categories(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    categories = db.query(Category).offset(skip).limit(limit).all()
    total = db.query(Category).count()

    return {
        "message": "Get categories list successfully",
        "data": categories,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get(
    "/{category_id}",
    response_model=dict,
    summary="Get category detail",
    status_code=status.HTTP_200_OK,
)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    return {"message": "Get category detail successfully", "data": category}


@router.post(
    "/",
    response_model=dict,
    summary="Create category",
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category_create: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if category with same name exists
    if db.query(Category).filter(Category.name == category_create.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists",
        )

    try:
        # Create new category
        category_data = category_create.model_dump()
        db_category = Category(**category_data)

        # Handle parent category if specified
        if category_create.parent_id:
            parent = (
                db.query(Category)
                .filter(Category.id == category_create.parent_id)
                .first()
            )
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with ID {category_create.parent_id} not found",
                )

        db.add(db_category)
        db.commit()
        db.refresh(db_category)

        return {"message": "Create category successfully", "data": db_category}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put(
    "/{category_id}",
    response_model=dict,
    summary="Update category",
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if category exists
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    try:
        # Check name uniqueness if name is being updated
        if category_update.name and category_update.name != db_category.name:
            if db.query(Category).filter(Category.name == category_update.name).first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists",
                )

        # Check parent_id validity if it's being updated
        if category_update.parent_id:
            # Prevent self-referencing
            if category_update.parent_id == category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category cannot be its own parent",
                )

            # Check if parent exists
            parent = (
                db.query(Category)
                .filter(Category.id == category_update.parent_id)
                .first()
            )
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with ID {category_update.parent_id} not found",
                )

        # Update category
        update_data = category_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)

        db.commit()
        db.refresh(db_category)

        return {"message": "Update category successfully", "data": db_category}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{category_id}",
    response_model=dict,
    summary="Delete category",
    status_code=status.HTTP_200_OK,  # Changed from 204 to 200 to allow response body
)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    # Check if category exists
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    # Check if category has children
    if db.query(Category).filter(Category.parent_id == category_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with subcategories. Delete subcategories first.",
        )

    try:
        db.delete(db_category)
        db.commit()
        return {"message": "Delete category successfully", "data": {"id": category_id}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
