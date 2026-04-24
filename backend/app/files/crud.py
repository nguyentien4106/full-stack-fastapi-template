import uuid

from sqlmodel import Session, select

from app.files.models import File, FileJob
from app.files.schemas import FileCreate, FileJobCreate


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


# ---------------------------------------------------------------------------
# FileJob CRUD
# ---------------------------------------------------------------------------

def create_file_job(*, session: Session, file_job_in: FileJobCreate) -> FileJob:
    db_file_job = FileJob.model_validate(file_job_in)
    session.add(db_file_job)
    session.commit()
    session.refresh(db_file_job)
    return db_file_job


def get_file_job_by_file_id(*, session: Session, file_id: uuid.UUID) -> FileJob | None:
    statement = select(FileJob).where(FileJob.file_id == file_id)
    return session.exec(statement).first()


def get_file_job_by_job_id(*, session: Session, job_id: str) -> FileJob | None:
    statement = select(FileJob).where(FileJob.job_id == job_id)
    return session.exec(statement).first()


def update_file_job(
    *,
    session: Session,
    file_job: FileJob,
    state: str,
    total_pages: int | None = None,
    extracted_pages: int | None = None,
    json_url: str | None = None,
    markdown_url: str | None = None,
    err_msg: str | None = None,
) -> FileJob:
    file_job.state = state
    if total_pages is not None:
        file_job.total_pages = total_pages
    if extracted_pages is not None:
        file_job.extracted_pages = extracted_pages
    if json_url is not None:
        file_job.json_url = json_url
    if markdown_url is not None:
        file_job.markdown_url = markdown_url
    if err_msg is not None:
        file_job.err_msg = err_msg
    session.add(file_job)
    session.commit()
    session.refresh(file_job)
    return file_job
