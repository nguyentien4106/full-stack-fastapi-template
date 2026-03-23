import json
from sqlalchemy import update, null
from app.models import FileCreate, File
from app.api.deps import SessionDep, CurrentUser

from fastapi import APIRouter, HTTPException, FastAPI, File, UploadFile
from app.helpers.s3 import upload_r2_file
router = APIRouter(prefix="/files", tags=["files"])

@router.post("/")
def upload_file(
     *, session: SessionDep, file: UploadFile = File()
):
    """
    Upload a file.

    This is a placeholder endpoint. In a real application, you would implement file upload logic here,
    such as generating a presigned URL for S3/R2 or handling multipart form data.
    """
    response = upload_r2_file('agr_sample1.png', file.file.read(), content_type=file.content_type)
    return {
          "filename": file.filename,
          "content_type": file.content_type,
          "size": len(file.file.read()),  # Note: This reads the entire file into memory, which may not be ideal for large files.
          "s3_response": response,
    }
    return None