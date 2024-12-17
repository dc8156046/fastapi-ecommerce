from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_superuser, get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get("/", summary="Get categories list")
async def get_categories(
    db=Depends(get_db), current_user=Depends(get_current_active_superuser)
):
    categories = db.query(Category).all()
    return {"message": "Get categories list successfully", "data": categories}


@router.get("/{category_id}", summary="Get category detail")
async def get_category(
    category_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    return {"message": "Get category detail successfully", "data": category}


@router.post("/", summary="Create category")
async def create_category(
    category: CategoryCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.add(Category(**category.dict()))
    db.commit()
    db.refresh(category)
    return {"message": "Create a category successfully", "data": category}


@router.put("/{category_id}", summary="Update category")
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(Category).filter(Category.id == category_id).update(category.dict())
    db.commit()
    return {"message": f"Update category successfully, category ID: {category_id}"}


@router.delete("/{category_id}", summary="Delete category")
async def delete_category(
    category_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(Category).filter(Category.id == category_id).delete()
    db.commit()
    return {"message": f"Delete category successfully, category ID: {category_id}"}
