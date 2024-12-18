import os
import uuid
from pathlib import Path
from fastapi import UploadFile
from PIL import Image


class ImageUploader:
    """Image uploader"""

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_image(self, file: UploadFile) -> tuple[str, int, int]:
        """
        Save image file and return file path, width, and height.

        Args:
            file: UploadFile: File to save

        Returns:
            tuple: File path, width, and height
        """
        # Generate filename
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = self.upload_dir / filename

        # Save image file
        image_data = await file.read()
        with open(file_path, "wb") as f:
            f.write(image_data)

        # Get image width and height
        with Image.open(file_path) as img:
            width, height = img.size

        return str(file_path), width, height
