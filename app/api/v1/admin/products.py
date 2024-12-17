from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_superuser, get_db
from app.schemas.product import ProductCreate
from app.models.product import Product

router = APIRouter()


@router.get("/", summary="Get products list")
async def get_products(
    db=Depends(get_db), current_user=Depends(get_current_active_superuser)
):
    products = db.query(Product).all()
    return {"message": "Get products list successfully", "data": products}


@router.get("/{product_id}", summary="Get product detail")
async def get_product(
    product_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    return {"message": "Get product detail successfully", "data": product}


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


@router.put("/{product_id}", summary="Update product")
async def update_product(
    product_id: int,
    product: ProductCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(Product).filter(Product.id == product_id).update(product.dict())
    db.commit()
    return {"message": f"Update product successfully, product ID: {product_id}"}


@router.delete("/{product_id}", summary="Delete product")
async def delete_product(
    product_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(Product).filter(Product.id == product_id).delete()
    db.commit()
    return {"message": f"Delete product successfully, product ID: {product_id}"}
