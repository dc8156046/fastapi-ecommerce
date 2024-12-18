from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Tuple
from fastapi import UploadFile
from PIL import Image
import io


class BaseStorage(ABC):
    """Base storage class"""

    @abstractmethod
    async def upload_file(self, file: BinaryIO, filename: str) -> str:
        """Upload file to storage service"""
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """Delete file from storage service"""
        pass

    @abstractmethod
    def get_file_url(self, filename: str) -> str:
        """Get file URL"""
        pass

    async def process_image(self, file: UploadFile) -> Tuple[BinaryIO, int, int]:
        """Process image file"""
        content = await file.read()
        img = Image.open(io.BytesIO(content))

        # Resize image
        # processed_img = img.resize((800, 800))

        # Save processed image to byte array
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format)
        img_byte_arr.seek(0)

        return img_byte_arr, img.width, img.height
