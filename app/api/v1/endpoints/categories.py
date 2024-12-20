from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from math import ceil
from app.models.category import Category
from app.models.product import Product
from app.api.deps import get_db
from app.schemas.category import CategoryResponse, PaginatedProductResponse

router = APIRouter()


@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Get categories list",
    status_code=status.HTTP_200_OK,
)
def get_categories(
    skip: int = 0,
    limit: int = 15,
    db: Session = Depends(get_db),
):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return {"message": "Get categories list successfully", "data": categories}


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category detail",
    status_code=status.HTTP_200_OK,
)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )
    return {"message": "Get category detail successfully", "data": category}


@router.get(
    "/{category_id}/products",
    response_model=PaginatedProductResponse,
    summary="Get products by category",
    status_code=status.HTTP_200_OK,
)
def get_products_by_category(
    category_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, gt=0),
    size: int = Query(10, gt=0),
    sort: Optional[str] = Query(None, regex="^(price|name|created_at)_(asc|desc)$"),
    is_active: Optional[bool] = Query(True),
):
    # Check if category exists
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.is_active == True)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found",
        )

    # Build base query
    query = db.query(Product).filter(
        Product.category_id == category_id, Product.is_active == is_active
    )

    # Apply sorting if specified
    if sort:
        field, direction = sort.split("_")
        order_by = getattr(Product, field)
        if direction == "desc":
            order_by = order_by.desc()
        query = query.order_by(order_by)

    # Get total count for pagination
    total = query.count()

    # Calculate pagination
    total_pages = ceil(total / size)
    if page > total_pages and total_pages > 0:
        page = total_pages

    # Apply pagination
    products = query.offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": total_pages,
        "items": products,
    }
