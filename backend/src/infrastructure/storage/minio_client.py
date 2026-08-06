"""MinIO storage client for evidence file storage."""
import hashlib
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from minio import Minio
from minio.error import S3Error

from ...config import get_settings

logger = logging.getLogger(__name__)


class MinIOStorageClient:
    """Client for MinIO object storage operations."""

    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        secure: bool = None,
        bucket: str = None,
    ):
        settings = get_settings()
        self.endpoint = endpoint or settings.MINIO_ENDPOINT
        self.access_key = access_key or settings.MINIO_ACCESS_KEY
        self.secret_key = secret_key or settings.MINIO_SECRET_KEY
        self.secure = secure if secure is not None else settings.MINIO_SECURE
        self.bucket = bucket or settings.MINIO_BUCKET

        self._client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

    def ensure_bucket_exists(self) -> bool:
        """Ensure the bucket exists, create if not."""
        try:
            if not self._client.bucket_exists(self.bucket):
                self._client.make_bucket(self.bucket)
                logger.info(f"Created MinIO bucket: {self.bucket}")
            return True
        except S3Error as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            return False

    def upload_file(
        self,
        object_name: str,
        file_data: bytes,
        content_type: str = "application/octet-stream",
    ) -> bool:
        """Upload file data to MinIO."""
        try:
            from io import BytesIO
            self._client.put_object(
                self.bucket,
                object_name,
                BytesIO(file_data),
                length=len(file_data),
                content_type=content_type,
            )
            logger.info(f"Uploaded object: {object_name} ({len(file_data)} bytes)")
            return True
        except S3Error as e:
            logger.error(f"Failed to upload object {object_name}: {e}")
            return False

    def download_file(self, object_name: str) -> Optional[bytes]:
        """Download file data from MinIO."""
        try:
            response = self._client.get_object(self.bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            logger.info(f"Downloaded object: {object_name} ({len(data)} bytes)")
            return data
        except S3Error as e:
            logger.error(f"Failed to download object {object_name}: {e}")
            return None

    def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO."""
        try:
            self._client.remove_object(self.bucket, object_name)
            logger.info(f"Deleted object: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Failed to delete object {object_name}: {e}")
            return False

    def file_exists(self, object_name: str) -> bool:
        """Check if file exists in MinIO."""
        try:
            self._client.stat_object(self.bucket, object_name)
            return True
        except S3Error:
            return False

    def get_file_url(self, object_name: str, expires: int = 3600) -> Optional[str]:
        """Generate a presigned URL for file access."""
        try:
            from datetime import timedelta
            url = self._client.presigned_get_object(
                self.bucket, object_name, expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    def compute_hash(self, file_data: bytes) -> str:
        """Compute SHA256 hash of file data."""
        return hashlib.sha256(file_data).hexdigest()

    def verify_hash(self, object_name: str, expected_hash: str) -> bool:
        """Verify the SHA256 hash of a stored file."""
        data = self.download_file(object_name)
        if data is None:
            return False
        return self.compute_hash(data) == expected_hash


# Module-level client instance
_minio_client: Optional[MinIOStorageClient] = None


def get_minio_client() -> MinIOStorageClient:
    """Get the singleton MinIO client instance."""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOStorageClient()
    return _minio_client


@asynccontextmanager
async def minio_storage() -> AsyncGenerator[MinIOStorageClient, None]:
    """Async context manager for MinIO storage."""
    client = get_minio_client()
    yield client