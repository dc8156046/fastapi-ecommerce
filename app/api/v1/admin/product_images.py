import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_superuser, get_db
from app.models.product import ProductImage, Product
from app.utils.storage import get_storage_backend

router = APIRouter()
storage = get_storage_backend()


@router.post("/upload/")
async def upload_image(
    file: UploadFile = File(...),
    product_id: int = Form(...),
    alt_text: str = Form(None),
    main_image: bool = Form(False),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """上传产品图片到云存储"""
    # 验证产品
    if not db.query(Product).filter(Product.id == product_id).first():
        raise HTTPException(status_code=404, detail="Product not found")

    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # 处理图片
        image_data, width, height = await storage.process_image(file)

        # 生成唯一文件名
        ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"

        # 上传到云存储
        file_url = await storage.upload_file(image_data, filename)

        # 更新主图状态
        if main_image:
            db.query(ProductImage).filter(ProductImage.product_id == product_id).update(
                {"main_image": False}
            )

        # 创建数据库记录
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


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_superuser),
):
    """删除云存储中的产品图片"""
    image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # 从云存储删除文件
        await storage.delete_file(image.image_url)

        # 删除数据库记录
        db.delete(image)
        db.commit()

        return {"message": "Image deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
