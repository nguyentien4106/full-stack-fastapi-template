from fastapi import HTTPException, status

ItemNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found",
)

InsufficientPermissionsException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions",
)
