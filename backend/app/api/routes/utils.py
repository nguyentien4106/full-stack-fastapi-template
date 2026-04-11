from fastapi import APIRouter, Depends, HTTPException
from pydantic.networks import EmailStr
from sqlalchemy import delete
from sqlmodel import Session

from app.aws.client import get_s3_client
from app.aws.config import aws_settings
from app.auth.dependencies import get_current_active_superuser, get_db
from app.files.models import File
from app.users.schemas import Message
from app.users.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.post(
    "/clear-files/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=200,
)
def clear_all_files(session: Session = Depends(get_db)) -> Message:
    """Remove all objects from the configured R2 bucket and delete File rows.

    Requires superuser. This is a destructive operation.
    """
    bucket = aws_settings.R2_BUCKET_NAME
    if not bucket:
        raise HTTPException(status_code=500, detail="R2 bucket not configured")

    client = get_s3_client()

    # List all objects in the bucket and delete them in batches of up to 1000
    try:
        paginator_args = {"Bucket": bucket}
        keys_to_delete: list[dict[str, str]] = []
        resp = client.list_objects_v2(**paginator_args)
        while True:
            contents = resp.get("Contents") or []
            for obj in contents:
                keys_to_delete.append({"Key": obj["Key"]})

            # If we have 1000 keys, delete them now
            if len(keys_to_delete) >= 1000:
                client.delete_objects(Bucket=bucket, Delete={"Objects": keys_to_delete})
                keys_to_delete = []

            if not resp.get("IsTruncated"):
                break
            resp = client.list_objects_v2(Bucket=bucket, ContinuationToken=resp.get("NextContinuationToken"))

        if keys_to_delete:
            client.delete_objects(Bucket=bucket, Delete={"Objects": keys_to_delete})
    except Exception as exc:  # pragma: no cover - depends on external service
        raise HTTPException(status_code=500, detail=f"Failed to clear R2 bucket: {exc}")

    # Delete all File rows in the database
    try:
        statement = delete(File)
        session.exec(statement)
        session.commit()
    except Exception as exc:  # pragma: no cover - db issue
        raise HTTPException(status_code=500, detail=f"Failed to delete File records: {exc}")

    return Message(message="Cleared all objects from R2 bucket and deleted File records")

