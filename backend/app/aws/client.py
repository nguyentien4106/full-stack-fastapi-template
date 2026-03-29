from __future__ import annotations
from alembic.autogenerate.api import log
from app.backend_pre_start import logger
from sqlalchemy.testing.plugin.plugin_base import pre

import boto3
from botocore.client import Config

from app.aws.config import aws_settings


def get_s3_client():
    """Return a boto3 S3 client configured for S3-compatible endpoints (e.g., Cloudflare R2)."""
    kwargs: dict = {}
    if aws_settings.R2_ACCESS_KEY:
        kwargs["aws_access_key_id"] = aws_settings.R2_ACCESS_KEY
    if aws_settings.R2_SECRET_KEY:
        kwargs["aws_secret_access_key"] = aws_settings.R2_SECRET_KEY

    endpoint = f"https://{aws_settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    client_config = Config(signature_version="s3v4")

    return boto3.client("s3", endpoint_url=endpoint, config=client_config, **kwargs)


def generate_presigned_put_url(key: str, bucket: str | None = None, expiration: int = 60*60*24*7) -> str:
    bucket = bucket or aws_settings.R2_BUCKET_NAME
    if not bucket:
        raise RuntimeError("S3 bucket not configured")

    client = get_s3_client()
    params = {"Bucket": bucket, "Key": key}
    logger.info(f"Generating presigned PUT URL for bucket {bucket} and key {key} with expiration {expiration} seconds")
    url = client.generate_presigned_url(
        ClientMethod="get_object", Params=params, ExpiresIn=expiration
    )
    logger.info(f"Generated presigned URL for key {key}: {url}")
    return url


def upload_file_to_r2(key: str, data: bytes, bucket: str | None = None, content_type: str | None = None, presign: bool = False) -> dict:
    bucket = bucket or aws_settings.R2_BUCKET_NAME
    if not bucket:
        raise RuntimeError("S3 bucket not configured")

    client = get_s3_client()
    extra_args: dict = {}
    if content_type:
        extra_args["ContentType"] = content_type

    logger.info(f"Uploading file to R2 with key {key} and content type {content_type}")
    resp = client.put_object(Bucket=bucket, Key=key, Body=data, **extra_args)
    logger.info(f"Uploaded file to R2 with key {key}")
    if presign:
        resp["PresignedURL"] = generate_presigned_put_url(key=key, bucket=bucket)

    return resp
