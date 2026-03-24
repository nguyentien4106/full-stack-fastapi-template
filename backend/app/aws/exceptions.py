from fastapi import HTTPException, status

S3BucketNotConfiguredException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="S3 bucket not configured",
)
