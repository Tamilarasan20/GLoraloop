from pathlib import Path

import boto3

from app.config import settings


class AssetStorageService:
    def upload_file(self, path: str | Path, key: str | None = None, content_type: str | None = None) -> str:
        file_path = Path(path)
        object_key = key or file_path.name

        if not self._r2_enabled():
            return f"/artifacts/{object_key}"

        client = boto3.client(
            "s3",
            endpoint_url=settings.r2_endpoint_url,
            aws_access_key_id=settings.r2_access_key_id,
            aws_secret_access_key=settings.r2_secret_access_key,
        )
        extra_args = {"ContentType": content_type} if content_type else {}
        client.upload_file(str(file_path), settings.r2_bucket, object_key, ExtraArgs=extra_args)
        base_url = settings.r2_public_base_url.rstrip("/") if settings.r2_public_base_url else ""
        return f"{base_url}/{object_key}" if base_url else object_key

    def _r2_enabled(self) -> bool:
        return all(
            [
                settings.r2_endpoint_url,
                settings.r2_access_key_id,
                settings.r2_secret_access_key,
                settings.r2_bucket,
            ]
        )
