from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ImageBase(BaseModel):
    product_id: int
    image_url: str
    alt_text: Optional[str] = None
    sort_order: Optional[int] = 0
    main_image: Optional[bool] = False
    is_active: Optional[bool] = True


class ImageCreate(ImageBase):
    pass


class ImageUpdate(ImageBase):
    pass


class ImageResponse(ImageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
