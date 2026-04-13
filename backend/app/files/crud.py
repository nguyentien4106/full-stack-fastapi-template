import uuid

from sqlmodel import Session

from app.files.models import File
from app.files.schemas import FileCreate


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

def update_file_info(
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