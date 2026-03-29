import io
from app.files.utils import get_df_from_result_json
from app.aws.config import aws_settings
from app.aws.client import generate_presigned_put_url
import uuid
from urllib.parse import quote
from app.files.dependencies import CurrentUser, SessionDep

from sqlmodel import Session

from app.files.models import File
from app.files.schemas import FileCreate

import pandas as pd  # type: ignore[import]


def create_file(*, session: Session, file_in: FileCreate, user_id: uuid.UUID) -> File:
    db_file = File.model_validate(file_in, update={"user_id": user_id})
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    return db_file

def delete_file(*, session: Session, file_id: uuid.UUID) -> None:
    db_file = session.get(File, file_id)
    if db_file:
        session.delete(db_file)
        session.commit()

def update_file_job_status(
    session: Session, file_id: uuid.UUID, job_status: str, job_id: str | None = None, err_msg : str | None = None
) -> File | None:
    db_file: File | None = session.get(File, file_id)
    if db_file:
        db_file.job_status = job_status
        if job_id:
            db_file.job_id = job_id
        if err_msg:
            db_file.err_msg = err_msg
        session.add(db_file)
        session.commit()
        session.refresh(db_file)
        return db_file
    return None

def download_excel_file(file: File, user: CurrentUser) -> tuple[bytes, str]:
    """
    Given a File record, download the file content from its URL and return as bytes.
    """
    json_key = f"{user.email}/{file.id}/result.json"
    presigned_url = generate_presigned_put_url(key=json_key, bucket=aws_settings.R2_BUCKET_NAME, expiration=3600)

    df = get_df_from_result_json(presigned_url)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:  # type: ignore[abstract]
        df.to_excel(writer, index=False, sheet_name="OCR Tables")
    excel_bytes = output.getvalue()

    safe_name = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename
    excel_filename = f"{safe_name}_tables.xlsx"

    # RFC 5987: percent-encode the UTF-8 filename for the filename* parameter
    encoded_filename = quote(excel_filename, safe="")
    content_disposition = (
        f"attachment; filename=\"tables.xlsx\"; "
        f"filename*=UTF-8''{encoded_filename}"
    )

    return (excel_bytes, content_disposition)