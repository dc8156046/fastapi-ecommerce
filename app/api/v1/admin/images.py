import os
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_superuser, get_db
from app.models.product import ProductImage, Product
from app.schemas.product import ImageUploadRequest, ImageResponse
from app.utils.upload import ImageUploader

router = APIRouter()
uploader = ImageUploader()


@router.post("/upload/", summary="Upload product image", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    product_id: int = Form(...),
    alt_text: Optional[str] = Form(None),
    main_image: bool = Form(False),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """Upload product image"""
    # Verify product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Save image
        file_path, width, height = await uploader.save_image(file)

        # Get image size
        image_size = os.path.getsize(file_path)

        # if main_image is True, set other images to False
        if main_image:
            db.query(ProductImage).filter(ProductImage.product_id == product_id).update(
                {"main_image": False}
            )

        # Save image to database
        image = ProductImage(
            product_id=product_id,
            image_url=file_path,
            alt_text=alt_text,
            main_image=main_image,
            sort_order=sort_order,
            width=width,
            height=height,
            image_size=image_size,
        )

        db.add(image)
        db.commit()
        db.refresh(image)

        return image

    except Exception as e:
        # Delete file if an error occurs
        if "file_path" in locals():
            os.unlink(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/product/{product_id}/images",
    summary="Get product images",
    response_model=List[ImageResponse],
)
async def get_product_images(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """Get product images"""
    images = (
        db.query(ProductImage)
        .filter(ProductImage.product_id == product_id)
        .order_by(ProductImage.sort_order)
        .all()
    )
    return images


@router.delete("/{image_id}", summary="Delete product image")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """Delete product image"""
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # delete image file
        if os.path.exists(image.image_url):
            os.unlink(image.image_url)

        # delete image from database
        db.delete(image)
        db.commit()

        return {"message": "Image deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{image_id}", summary="Update product image", response_model=ImageResponse)
async def update_image(
    image_id: int,
    alt_text: Optional[str] = Form(None),
    main_image: bool = Form(False),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """Update product image"""
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # if main_image is True, set other images to False
    if main_image and not image.main_image:
        db.query(ProductImage).filter(
            ProductImage.product_id == image.product_id
        ).update({"main_image": False})

    # Update image
    image.alt_text = alt_text
    image.main_image = main_image
    image.sort_order = sort_order

    db.commit()
    db.refresh(image)

    return image
