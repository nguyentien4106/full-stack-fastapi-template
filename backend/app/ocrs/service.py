import logging

import requests
from sqlmodel import Session

from app.aws.client import upload_file_to_r2
from app.core.config import settings
from app.files.models import File
from app.files.service import update_file_job_info
from app.ocrs.constants import OcrJobStatus
from app.ocrs.dependencies import CurrentUser, SessionDep
from app.ocrs.schemas import OcrJobResponse, OcrSubmitResponse
from app.storages.service import increment_storage_stat
from app.utils import get_bytes_from_file_url

logger = logging.getLogger(__name__)

def upload_ocr_job(session: Session, file: File, file_url: str) -> tuple[bool, str | None]:
    """
    Submit an OCR job for the given file URL and update job_id / job_status
    on the File record. Only posts the job — polling is handled separately.
    """

    headers = {
        "Authorization": f"bearer {settings.OCR_API_TOKEN}",
        "Content-Type": "application/json",
    }

    optional_payload = {
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }

    payload = {
        "fileUrl": file_url,
        "model": settings.OCR_MODEL,
        "optionalPayload": optional_payload,
    }
    raw = requests.post(str(settings.OCR_JOB_URL), json=payload, headers=headers)
    raw.raise_for_status()

    submit_response = OcrSubmitResponse.model_validate(raw.json())
    is_success = submit_response.code == 0

    update_file_job_info(
        session,
        file.id,
        job_status=OcrJobStatus.RUNNING if is_success else OcrJobStatus.FAILED,
        job_id=submit_response.data.jobId,
        err_msg=None if is_success else submit_response.msg
    )

    return (is_success, submit_response.data.jobId if is_success else None)

def update_ocr_job_status(file: File, session: SessionDep, user: CurrentUser) -> OcrJobResponse:
    """
    Poll the OCR API for job results. Returns a typed OcrJobResponse.
    """
    if file.job_status == OcrJobStatus.DONE or file.job_status == OcrJobStatus.FAILED:
        logger.info("File %s already has job status %s, skipping OCR job status update", file.id, file.job_status)
        return OcrJobResponse(code=0, msg="Job already completed", data=None)  # ty:ignore[call-arg]  # ty:ignore[invalid-argument-type]

    headers = {"Authorization": f"bearer {settings.OCR_API_TOKEN}"}
    raw = requests.get(f"{settings.OCR_JOB_URL}/{file.job_id}", headers=headers)
    assert raw.status_code in (200, 404), f"OCR API returned unexpected status code {raw.status_code}"
    result: OcrJobResponse = OcrJobResponse.model_validate(raw.json())

    if not result.code == 0:
        logger.error("Error fetching OCR job status for job_id %s: %s", file.job_id, result.msg)
        update_file_job_info(session, file_id=file.id, job_status=OcrJobStatus.FAILED, err_msg=result.msg)
        return result

    state = result.data.state
    if state != OcrJobStatus.PENDING:
        update_file_job_info(session, file_id=file.id, job_status=state)  # Update all files with this job_id

    if state == OcrJobStatus.DONE:
        key = f"{user.email}/{file.id}/result.json"
        (json_url, md_url) = (result.data.resultUrl.jsonUrl, result.data.resultUrl.markdownUrl) if result.data.resultUrl else (None, None)
        if json_url:
            upload_file_to_r2(key=key, data=get_bytes_from_file_url(json_url), content_type="application/json")
        if result.data.extractProgress:
            logger.info("OCR job %s progress: %s", file.job_id, result.data.extractProgress)
            increment_storage_stat(
                session=session,
                user_id=user.id,
                size_delta=file.size,
                total_pages_delta=result.data.extractProgress.extractedPages,
            )  # Increment extracted pages in storage stat
        logger.info("OCR job %s completed successfully. Result URLs - JSON: %s, Markdown: %s", file.job_id, json_url, md_url)

    elif state == OcrJobStatus.FAILED:
        logger.error("OCR job %s failed: %s", file.job_id, result.data.errorMsg)
        update_file_job_info(session, file_id=file.id, job_status=OcrJobStatus.FAILED, err_msg=result.data.errorMsg)

    return result

def get_job_status(job_id: str) -> object:
    """
    Get the current status of an OCR job by job ID. Returns a typed OcrJobResponse.
    """
    headers = {"Authorization": f"bearer {settings.OCR_API_TOKEN}"}
    raw = requests.get(f"{settings.OCR_JOB_URL}/{job_id}", headers=headers)
    assert raw.status_code in (200, 404), f"OCR API returned unexpected status code {raw.status_code}"
    return raw.json()