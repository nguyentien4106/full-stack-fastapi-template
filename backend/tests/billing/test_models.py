import uuid
from datetime import datetime

from app.billing.models import MonthlyUsage
from app.files.models import FileJob


def test_monthly_usage_fields() -> None:
    uid = uuid.uuid4()
    usage = MonthlyUsage(user_id=uid, year_month=202606, pages_used=10)
    assert usage.user_id == uid
    assert usage.year_month == 202606
    assert usage.pages_used == 10
    assert usage.__tablename__ == "monthly_usage"
    assert isinstance(usage.id, uuid.UUID)
    assert isinstance(usage.updated_at, datetime)


def test_monthly_usage_pages_used_defaults_to_zero() -> None:
    usage = MonthlyUsage(user_id=uuid.uuid4(), year_month=202606)
    assert usage.pages_used == 0


def test_file_job_billed_at_defaults_to_none() -> None:
    job = FileJob(job_id="job-1", file_id=uuid.uuid4())
    assert job.billed_at is None
