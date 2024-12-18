import boto3
from botocore.exceptions import ClientError
from app.core.config import StorageSettings
from app.utils.storage.base import BaseStorage
from typing import BinaryIO


class S3Storage(BaseStorage):
    """AWS S3 storage class"""

    def __init__(self):
        settings = StorageSettings()
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        self.bucket_name = settings.AWS_BUCKET_NAME

    async def upload_file(self, file: BinaryIO, filename: str) -> str:
        """Upload file to S3"""
        try:
            self.s3_client.upload_fileobj(
                file, self.bucket_name, filename, ExtraArgs={"ACL": "public-read"}
            )
            return self.get_file_url(filename)
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

    async def delete_file(self, file_url: str) -> bool:
        """Delete file from S3"""
        try:
            filename = file_url.split("/")[-1]
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
            return True
        except ClientError as e:
            raise Exception(f"Failed to delete file from S3: {str(e)}")

    def get_file_url(self, filename: str) -> str:
        """Get file URL"""
        return f"https://{self.bucket_name}.s3.amazonaws.com/{filename}"
