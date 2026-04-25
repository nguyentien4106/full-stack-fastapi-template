from fastapi import HTTPException, status

FileNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="File not found",
)

FileTooLargeException = HTTPException(
    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    detail="File too large",
)

NoTableFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="No table found in the file",
)