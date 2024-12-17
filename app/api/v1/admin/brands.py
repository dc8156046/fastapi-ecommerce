from fastapi import APIRouter, Depends
from app.schemas.brand import BrandCreate
from app.api.deps import get_current_active_superuser, get_db
from app.models.brand import Brand

router = APIRouter()


# get brands list
@router.get("/", summary="Get brands list")
async def get_brands(
    db=Depends(get_db), current_user=Depends(get_current_active_superuser)
):
    brands = db.query(Brand).all()
    return {"message": "Get brands list successfully", "data": brands}


# get brand detail
@router.get("/{brand_id}", summary="Get brand detail")
async def get_brand(
    brand_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    return {"message": "Get brand detail successfully", "data": brand}


# create brand
@router.post("/", summary="Create brand")
async def create_brand(
    brand: BrandCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.add(Brand(**brand.dict()))
    db.commit()
    db.refresh(brand)
    return {"message": "Create a brand successfully", "data": brand}


# delete brand
@router.delete("/{brand_id}", summary="Delete brand")
async def delete_brand(
    brand_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(Brand).filter(Brand.id == brand_id).delete()
    db.commit()
    return {"message": f"Delete brand successfully, brand ID: {brand_id}"}
