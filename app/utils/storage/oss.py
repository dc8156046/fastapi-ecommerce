import oss2
from app.core.config import StorageSettings
from app.utils.storage.base import BaseStorage
from typing import BinaryIO


class OSSStorage(BaseStorage):
    """阿里云OSS存储实现"""

    def __init__(self):
        settings = StorageSettings()
        auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID, settings.ALIYUN_ACCESS_KEY_SECRET
        )
        self.bucket = oss2.Bucket(
            auth, settings.ALIYUN_ENDPOINT, settings.ALIYUN_BUCKET_NAME
        )
        self.bucket_name = settings.ALIYUN_BUCKET_NAME

    async def upload_file(self, file: BinaryIO, filename: str) -> str:
        """上传文件到OSS"""
        try:
            self.bucket.put_object(filename, file)
            return self.get_file_url(filename)
        except oss2.exceptions.OssError as e:
            raise Exception(f"Failed to upload file to OSS: {str(e)}")

    async def delete_file(self, file_url: str) -> bool:
        """从OSS删除文件"""
        try:
            filename = file_url.split("/")[-1]
            self.bucket.delete_object(filename)
            return True
        except oss2.exceptions.OssError as e:
            raise Exception(f"Failed to delete file from OSS: {str(e)}")

    def get_file_url(self, filename: str) -> str:
        """获取OSS文件URL"""
        return f"https://{self.bucket_name}.{self.bucket.endpoint.replace('https://', '')}/{filename}"
