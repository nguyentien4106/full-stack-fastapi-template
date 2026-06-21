import uuid
from typing import Annotated

from fastapi import Depends, HTTPException

from app.auth.dependencies import (  # noqa: F401
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
    get_current_user,
)
from app.files.crud import get_file_job_by_file_id
from app.files.models import File, FileJob
from app.ocrs.constants import OcrJobStatus


def get_owned_file(file_id: uuid.UUID, session: SessionDep, user: CurrentUser) -> File:
    """Load a file by id, returning it only if it belongs to the current user.

    Raises 404 if the file does not exist and 403 if it is owned by someone else.
    """
    file = session.get(File, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if file.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this file"
        )
    return file


OwnedFile = Annotated[File, Depends(get_owned_file)]


def require_done_job(*, session: SessionDep, file_id: uuid.UUID) -> FileJob:
    """Return the file's OCR job, raising 400 unless it has finished successfully."""
    file_job = get_file_job_by_file_id(session=session, file_id=file_id)
    if not file_job or file_job.state != OcrJobStatus.DONE:
        raise HTTPException(status_code=400, detail="OCR job is not done yet")
    return file_job
