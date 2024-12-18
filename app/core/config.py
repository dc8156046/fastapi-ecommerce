from pydantic_settings import BaseSettings


class StorageSettings(BaseSettings):
    """Storage settings"""

    STORAGE_TYPE: str = "s3"  # Option: s3, oss, cos

    # AWS S3 configuration
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-northeast-1"
    AWS_BUCKET_NAME: str = ""

    # Aliyun OSS configuration
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_ENDPOINT: str = ""
    ALIYUN_BUCKET_NAME: str = ""
