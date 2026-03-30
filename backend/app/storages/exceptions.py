from fastapi import HTTPException, status

StorageStatNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Storage stat not found",
)
