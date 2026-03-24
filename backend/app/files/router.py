from fastapi import APIRouter, File, HTTPException, UploadFile

from app.aws.client import upload_file
from app.aws.config import aws_settings
from app.aws.schemas import PresignRequest, PresignResponse

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/")
def upload_file_endpoint(
    file: UploadFile = File()  # noqa: B008
):
    """
    Upload a file to R2/S3 storage.
    """
    file_bytes = file.file.read()
    response = upload_file(
        key=file.filename or "upload",
        data=file_bytes,
        content_type=file.content_type,
    )
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(file_bytes),
        "s3_response": response,
    }


@router.post("/presign", response_model=PresignResponse)
def presign_upload(req: PresignRequest):
    """
    Generate a presigned PUT URL for direct client uploads.
    """
    from app.aws.client import generate_presigned_put_url

    if not aws_settings.R2_BUCKET_NAME and not req.bucket:
        raise HTTPException(status_code=500, detail="S3 bucket not configured")

    key = req.filename
    try:
        url = generate_presigned_put_url(key=key, bucket=req.bucket, expiration=3600)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return PresignResponse(url=url, key=key)
