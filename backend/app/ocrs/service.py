from app.utils import get_bytes_from_file_url
from app.aws.client import upload_file_to_r2
import logging
import requests
from sqlmodel import Session
from app.core.config import settings
from app.files.models import File
from app.files.service import update_file_job_status
from app.ocrs.constants import OcrJobStatus
from app.ocrs.dependencies import SessionDep, CurrentUser
from app.ocrs.schemas import OcrJobResponse, OcrSubmitResponse, OcrJobResponse

logger = logging.getLogger(__name__)

def upload_ocr_job(session: Session, file: File, file_url: str) -> File:
    """
    Submit an OCR job for the given file URL and update job_id / job_status
    on the File record. Only posts the job — polling is handled separately.
    """
    logger.info(f"Starting OCR job submission for file {file.id} with URL {file_url}")

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
    logger.info(f"Submitting OCR job for file {file.id} with payload: {payload}")
    raw = requests.post(str(settings.OCR_JOB_URL), json=payload, headers=headers)
    logger.info(f"OCR job submission response for file {file.id}: {raw.status_code} - {raw.text}")
    raw.raise_for_status()
    logger.info(f"Submitted OCR job for file {file.id}, response: {raw.json()}")

    submit_response = OcrSubmitResponse.model_validate(raw.json())

    update_file_job_status(session, file.id, job_status=OcrJobStatus.RUNNING, job_id=submit_response.data.jobId)
    logger.info(f"Updated file {file.id} job status to {OcrJobStatus.RUNNING} with job ID {submit_response.data.jobId}")
    return file

def get_update_file_ocr(file: File, session: SessionDep, user: CurrentUser) -> OcrJobResponse:
    """
    Poll the OCR API for job results. Returns a typed OcrJobResponse.
    """
    headers = {"Authorization": f"bearer {settings.OCR_API_TOKEN}"}
    raw = requests.get(f"{settings.OCR_JOB_URL}/{file.job_id}", headers=headers)
    assert raw.status_code in (200, 404), f"OCR API returned unexpected status code {raw.status_code}"
    result: OcrJobResponse = OcrJobResponse.model_validate(raw.json())
    state = result.data.state
    if state != OcrJobStatus.PENDING:
        print(f"OCR job {file.job_id} status: {state}")
        update_file_job_status(session, file_id=file.id, job_status=state)  # Update all files with this job_id

    if state == OcrJobStatus.DONE:
        progress = result.data.extractProgress
        logger.info(
            "Job %s completed — pages: %s, start: %s, end: %s",
            file.job_id,
            progress.extractedPages if progress else None,
            progress.startTime if progress else None,
            progress.endTime if progress else None,
        )
        key = f"{user.email}/{file.id}/result.json"
        (json_url, md_url) = (result.data.resultUrl.jsonUrl, result.data.resultUrl.markdownUrl) if result.data.resultUrl else (None, None)
        if json_url:
            upload_file_to_r2(key=key, data=get_bytes_from_file_url(json_url), content_type="application/json")
        if md_url:
            upload_file_to_r2(key=key.replace(".json", ".md"), data=get_bytes_from_file_url(md_url), content_type="text/markdown")
    elif state == OcrJobStatus.FAILED:
        logger.error("OCR job %s failed: %s", file.job_id, result.data.errorMsg)
        update_file_job_status(session, file_id=file.id, job_status=OcrJobStatus.FAILED, err_msg=result.data.errorMsg)

    return result

def get_job_status(job_id: str) -> object:
    """
    Get the current status of an OCR job by job ID. Returns a typed OcrJobResponse.
    """
    headers = {"Authorization": f"bearer {settings.OCR_API_TOKEN}"}
    raw = requests.get(f"{settings.OCR_JOB_URL}/{job_id}", headers=headers)
    assert raw.status_code in (200, 404), f"OCR API returned unexpected status code {raw.status_code}"
    return raw.json()