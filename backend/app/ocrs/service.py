import logging

import requests
from sqlmodel import Session

from app.aws.client import upload_file_to_r2
from app.core.config import settings
from app.files.models import File
from app.files.service import update_file_info
from app.ocrs.constants import OcrJobStatus
from app.ocrs.dependencies import CurrentUser, SessionDep
from app.ocrs.schemas import OcrJobResponse, OcrSubmitResponse
from app.storages.service import increment_storage_stat
from app.utils import get_bytes_from_file_url

logger = logging.getLogger(__name__)

headers = {
    "Authorization": f"bearer {settings.OCR_API_TOKEN}",
    "Content-Type": "application/json",
}

optional_payload = {
    "useDocOrientationClassify": False,
    "useDocUnwarping": False,
    "useChartRecognition": False,
}

def post_ocr_jobs(session: Session, file: File, file_url: str) -> tuple[bool, str | None]:
    """
    Submit an OCR job for the given file URL and update job_id / job_status
    on the File record. Only posts the job — polling is handled separately.
    """

    payload = {
        "fileUrl": file_url,
        "model": settings.OCR_MODEL,
        "optionalPayload": optional_payload,
    }

    raw = requests.post(str(settings.OCR_JOB_URL), json=payload, headers=headers)
    raw.raise_for_status()
    logger.info("Submitted OCR job for file %s, response: %s", file.id, raw.text)
    submit_response = OcrSubmitResponse.model_validate(raw.json())
    is_success = submit_response.is_success()
    if not is_success:
        logger.error("Failed to submit OCR job for file %s: %s - %s", file.id, submit_response.code, submit_response.msg)
        return (False, None)

    job_id = submit_response.data.jobId
    logger.info("OCR job submitted successfully for file %s, job_id: %s", file.id, job_id)
    update_file_info(
        session,
        file_id=file.id,
        job_status=OcrJobStatus.RUNNING,
        job_id=job_id,
        err_msg=None
    )

    return (is_success, job_id)

def get_ocr_job_status(file: File, session: SessionDep, user: CurrentUser) -> str | None:
    """
    Poll the OCR API for job results. Returns a typed OcrJobResponse.
    """
    if not file.job_id:
        logger.error("File %s has no job_id but is being polled for OCR status", file.id)
        update_file_info(session, file_id=file.id, job_status=OcrJobStatus.FAILED, err_msg="No job_id for this file")
        raise Exception("No job_id for this file")

    if file.job_status == OcrJobStatus.DONE or file.job_status == OcrJobStatus.FAILED:
        return file.job_status

    headers = {"Authorization": f"bearer {settings.OCR_API_TOKEN}"}

    raw = requests.get(f"{settings.OCR_JOB_URL}/{file.job_id}", headers=headers)

    assert raw.status_code in (200, 404), f"OCR API returned unexpected status code {raw.status_code}"

    result: OcrJobResponse = OcrJobResponse.model_validate(raw.json())
    logger.info("get_ocr_job_status for file %s,\n result: %s", file.json(), result.json())
    if not result.is_success():
        logger.error("Error fetching OCR job status for job_id %s: %s", file.job_id, result.msg)
        update_file_info(session, file_id=file.id, job_status=OcrJobStatus.FAILED, err_msg=result.msg)
        raise Exception(f"OCR API error: {result.msg}")

    state = result.data.state
    logger.info("OCR job %s status: %s", file.job_id, state)
    if state == OcrJobStatus.RUNNING and file.job_status == OcrJobStatus.PENDING:
        update_file_info(session, file_id=file.id, job_status=OcrJobStatus.RUNNING)  # Update all files with this job_id

    elif state == OcrJobStatus.DONE:
        logger.info("OCR job %s completed successfully. Result uploaded to R2.", file.job_id)
        update_file_info(session, file_id=file.id, job_status=OcrJobStatus.DONE)
        upload_ocr_job_result(user=user, file=file, result=result, session=session)

    elif state == OcrJobStatus.FAILED:
        logger.error("OCR job %s failed: %s", file.job_id, result.data.errorMsg)
        update_file_info(session, file_id=file.id, job_status=OcrJobStatus.FAILED, err_msg=result.data.errorMsg)

    return state

def upload_ocr_job_result(user: CurrentUser, file: File, result: OcrJobResponse, session: SessionDep):
    key = f"{user.email}/{file.id}/result.json"
    (json_url, md_url) = (result.data.resultUrl.jsonUrl, result.data.resultUrl.markdownUrl) if result.data.resultUrl else (None, None)
    logger.info(f"Uploading OCR job result for file {file.id} to R2, json_url: {json_url}, md_url: {md_url}")
    if json_url:
        upload_file_to_r2(key=key, data=get_bytes_from_file_url(json_url), content_type="application/json")

    increment_storage_stat(
        session=session,
        user_id=user.id,
        size_delta=file.size,
        total_pages_delta=result.data.extractProgress.extractedPages,  # ty:ignore[unresolved-attribute]
        file_count_delta=1
    )