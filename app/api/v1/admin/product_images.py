import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_superuser, get_db
from app.models.product import ProductImage, Product
from app.utils.storage import get_storage_backend

router = APIRouter()
storage = get_storage_backend()


@router.post(
    "/upload/",
    summary="Upload product image to cloud storage",
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile = File(...),
    product_id: int = Form(...),
    alt_text: str = Form(None),
    main_image: bool = Form(False),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
    summary="Upload product image to cloud storage",
):
    """Upload product image"""
    # verify product exists
    if not db.query(Product).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")

    # verify file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # process image
        image_data, width, height = await storage.process_image(file)

        # generate filename
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        # upload file to storage
        file_url = await storage.upload_file(image_data, filename)

        # set other images to False if main_image is True
        if main_image:
            db.query(ProductImage).filter(ProductImage.product_id == product_id).update(
                {"main_image": False}
            )

        # save image to database
        image = ProductImage(
            product_id=product_id,
            image_url=file_url,
            alt_text=alt_text,
            main_image=main_image,
            sort_order=sort_order,
            width=width,
            height=height,
            image_size=len(image_data.getvalue()),
        )

        db.add(image)
        db.commit()
        db.refresh(image)

        return {"message": "Image uploaded successfully", "data": image}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{image_id}",
    summary="Delete product image",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
    summary="Delete product image from cloud storage",
):
    """Delete product image"""
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Delete file from storage
        await storage.delete_file(image.image_url)

        # delete image from database
        db.delete(image)
        db.commit()

        return {"message": "Image deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
