from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_superuser, get_db
from schemas.product import ProductCreate
from models.product import Product

router = APIRouter()


@router.post("/", summary="Create product")
async def create_product(
    product: ProductCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.add(Product(**product.dict()))
    db.commit()
    db.refresh(product)
    return {"message": "Create a product successfully", "data": product}


@router.delete("/{product_id}", summary="Delete product")
async def delete_product(
    product_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(Product).filter(Product.id == product_id).delete()
    db.commit()
    return {"message": f"Delete product successfully, product ID: {product_id}"}
