from fastapi import APIRouter, Depends
from app.api.deps import get_current_active_superuser, get_db
from app.models.product import ProductImage
from app.schemas.image import ImageCreate, ImageUpdate, ImageResponse

router = APIRouter()


@router.get("/", summary="Get images list")
async def get_images(
    offset=0,
    limit=10,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    images = db.query(ProductImage).offset(offset).limit(limit).all()
    return {"message": "Get images list successfully", "data": images}


@router.get("/product/{product_id}", summary="Get images list by product ID")
async def get_images_by_product_id(
    product_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    images = db.query(ProductImage).filter(ProductImage.product_id == product_id).all()
    return {"message": "Get images list by product ID successfully", "data": images}


@router.get("/{image_id}", summary="Get image detail", response_model=ImageResponse)
async def get_image(
    image_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    return {"message": "Get image detail successfully", "data": image}


@router.post("/", summary="Upload product image", response_model=ImageResponse)
async def create_image(
    image: ImageCreate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.add(ProductImage(**image.dict()))
    db.commit()
    db.refresh(image)
    return {"message": "Upload product image successfully", "data": image}


@router.put("/{image_id}", summary="Update image", response_model=ImageResponse)
async def update_image(
    image_id: int,
    image: ImageUpdate,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(ProductImage).filter(ProductImage.id == image_id).update(image.dict())
    db.commit()
    return {"message": f"Update product image successfully, image ID: {image_id}"}


@router.delete("/{image_id}", summary="Delete image")
async def delete_image(
    image_id: int,
    db=Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    db.query(ProductImage).filter(ProductImage.id == image_id).delete()
    db.commit()
    return {"message": f"Delete product image successfully, image ID: {image_id}"}
