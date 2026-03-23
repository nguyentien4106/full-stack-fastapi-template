from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.helpers import s3
from app.core.config import settings

router = APIRouter(prefix="/storage", tags=["storage"])


class PresignRequest(BaseModel):
    filename: str
    content_type: str | None = None
    # Optionally allow callers to choose a different bucket
    bucket: str | None = None


class PresignResponse(BaseModel):
    url: str
    key: str


@router.post("/presign", response_model=PresignResponse)
def presign_upload(req: PresignRequest):
    if not settings.R2_BUCKET_NAME and not req.bucket:
        raise HTTPException(status_code=500, detail="S3 bucket not configured")

    # Create an object key. In a real app you may want to namespace by user/id, add
    # random prefixes, validate filename, etc. Here we simply use the provided filename.
    key = req.filename

    try:
        url = s3.generate_presigned_put_url(key=key, bucket=req.bucket, expiration=3600)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return PresignResponse(url=url, key=key)
