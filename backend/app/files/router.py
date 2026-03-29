from app.backend_pre_start import logger
import uuid
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Response, UploadFile
from sqlmodel import select

from app.aws.client import upload_file_to_r2
from app.aws.config import aws_settings
from app.aws.schemas import PresignRequest, PresignResponse
from app.files.dependencies import CurrentUser, SessionDep
from app.files.models import File
from app.files.schemas import FileCreate, FilePublic, FilesPublic
from app.files.service import create_file, delete_file, update_file_job_status, download_excel_file
from app.ocrs.service import get_update_file_ocr, upload_ocr_job, get_job_status

from sqlalchemy import desc

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/", response_model=FilePublic)
def upload_file_endpoint(
    session: SessionDep,
    user: CurrentUser,
    file: UploadFile # noqa: B008,
):
    """
    Upload a file to R2/S3 storage.
    """
    file_bytes = file.file.read()
    file_name = file.filename or "upload"
    file_type = file.content_type or "application/octet-stream"
    file_create = FileCreate(filename=file_name, content_type=file_type, size=len(file_bytes), url="")
    file_result = create_file(session=session, file_in=file_create, user_id=user.id)

    try:
        logger.info(f"Created DB record for file {file_result.id} with name {file_name}")
        r2_result = upload_file_to_r2(
            key=user.email + "/" + str(file_result.id) + "/" + file_name,  # Use DB record ID for unique key
            data=file_bytes,
            content_type=file_type,
            presign=True
        )
        upload_ocr_job(session=session, file=file_result, file_url=r2_result["PresignedURL"])

        return file_result
    except Exception as exc:
        delete_file(session=session, file_id=file_result.id)  # Clean up DB record on failure
        logger.error(f"Error uploading file {file_name}: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/presign", response_model=PresignResponse)
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


@router.put("/{file_id}?job_status={job_status}")
def update_file_job_status_endpoint(
    file_id: uuid.UUID,
    job_status: str,
    session: SessionDep,
):
    """
    Update the job status for a file based on OCR job updates.
    """

    updated_file = update_file_job_status(session=session, file_id=file_id, job_status=job_status)
    if not updated_file:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "Job status updated", "file_id": str(updated_file.id), "job_status": updated_file.job_status}

@router.get("/{file_id}/status", response_model=FilePublic)
def get_file_status(file_id: uuid.UUID, session: SessionDep, user: CurrentUser):
    """
    Get the current status of a file, including OCR job status if applicable.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    ocr_result = get_update_file_ocr(file=file,  session=session, user=user)  # Poll OCR API for latest status
    file.job_status = ocr_result.data.state  # Update file status based on OCR job state
    return file

@router.get('/', response_model=FilesPublic)
def list_files(session: SessionDep, user: CurrentUser, skip: int = 0, limit: int = 0):
    """
    List all files uploaded by the current user.
    """
    user_id = user.id
    if limit <= 0:
        statement = select(File).where(File.user_id == user_id).order_by(desc(File.created_at))  # ty:ignore[invalid-argument-type]
    else:
        statement = select(File).where(File.user_id == user_id).order_by(desc(File.created_at)).offset(skip).limit(limit)  # ty:ignore[invalid-argument-type]

    files = session.exec(statement).all()

    return FilesPublic(data=files, count=len(files))  # ty:ignore[invalid-argument-type]

@router.post("/{file_id}/download")
def download_table_excel_file(file_id: uuid.UUID, session: SessionDep, user: CurrentUser):
    """
    Stream an Excel file built from the OCR result JSON stored in R2.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this file")
    if file.job_status != "done":
        raise HTTPException(status_code=400, detail="OCR job is not done yet")

    excel_bytes, content_disposition = download_excel_file(file=file, user=user)

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": content_disposition},
    )

@router.get("jobs/{job_id}/status")
def get_job_status_endpoint(job_id: str, session: SessionDep):
    """
    Get the status of an OCR job by job ID.
    """
    # This endpoint can be used by a background worker to poll OCR job status if needed
    # For now, we handle polling in the get_file_status endpoint, but this can be useful for more direct checks

    try:
        ocr_status = get_job_status(job_id=job_id)
        return {"job_id": job_id, "status": ocr_status}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))