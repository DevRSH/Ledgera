import boto3
import hashlib
import uuid
import magic
from botocore.config import Config
from app.core.config import settings

class StorageService:
    def __init__(self):
        if not settings.R2_ACCESS_KEY_ID:
            # Mock or dummy if not configured
            self.client = None
            return
            
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version="s3v4"),
            region_name="auto",
        )
        self.bucket = settings.R2_BUCKET_NAME

    async def upload(
        self,
        content: bytes,
        extension: str,
        tenant_id: str,
        tipo: str
    ) -> tuple[str, str]:
        """
        Uploads a file to storage. Returns (storage_key, hash_sha256).
        """
        if not self.client:
            # In development without R2, we could save to local disk
            # For now, let's just return a fake key
            return f"mock/{tenant_id}/{uuid.uuid4()}{extension}", hashlib.sha256(content).hexdigest()

        file_uuid = str(uuid.uuid4())
        key = f"tenants/{tenant_id}/{tipo}/{file_uuid}{extension}"
        hash_sha256 = hashlib.sha256(content).hexdigest()
        
        mime = magic.from_buffer(content, mime=True)
        
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
            ContentType=mime,
            Metadata={"sha256": hash_sha256, "tenant": str(tenant_id)}
        )
        return key, hash_sha256

    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generates a presigned URL for downloading."""
        if not self.client:
            return f"http://mock-storage/{key}"
            
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

storage_service = StorageService()
