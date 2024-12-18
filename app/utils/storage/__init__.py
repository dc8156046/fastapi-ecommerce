from app.core.config import StorageSettings
from app.utils.storage.s3 import S3Storage
from app.utils.storage.oss import OSSStorage
from app.utils.storage.base import BaseStorage


def get_storage_backend() -> BaseStorage:
    """Get storage backend based on settings"""
    settings = StorageSettings()

    if settings.STORAGE_TYPE == "s3":
        return S3Storage()
    elif settings.STORAGE_TYPE == "oss":
        return OSSStorage()
    else:
        raise ValueError(f"Unsupported storage type: {settings.STORAGE_TYPE}")
