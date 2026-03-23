from __future__ import annotations

import boto3
from botocore.client import Config

from app.core.config import settings

def _get_s3_client():
    """Return a boto3 S3 client configured for S3-compatible endpoints (e.g., Cloudflare R2)."""
    kwargs: dict = {}
    if settings.R2_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.R2_ACCESS_KEY
    if settings.R2_SECRET_KEY:
        kwargs["aws_secret_access_key"] = settings.R2_SECRET_KEY

    endpoint = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    client_config = Config(signature_version="s3v4")

    return boto3.client("s3", endpoint_url=endpoint, config=client_config, **kwargs)


def generate_presigned_put_url(key: str, bucket: str | None = None, expiration: int = 3600) -> str:
    bucket = bucket or settings.R2_BUCKET_NAME
    if not bucket:
        raise RuntimeError("S3 bucket not configured (S3_BUCKET)")

    client = _get_s3_client()
    params = {"Bucket": bucket, "Key": key}
    url = client.generate_presigned_url(
        ClientMethod="put_object", Params=params, ExpiresIn=expiration
    )
    return url


def upload_r2_file(key: str, data: bytes, bucket: str | None = None, content_type: str | None = None) -> dict:
    bucket = bucket or settings.R2_BUCKET_NAME
    if not bucket:
        raise RuntimeError("S3 bucket not configured (S3_BUCKET)")

    client = _get_s3_client()
    extra_args: dict = {}
    if content_type:
        extra_args["ContentType"] = content_type

    resp = client.put_object(Bucket=bucket, Key=key, Body=data, **extra_args)
    return resp
