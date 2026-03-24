from fastapi import HTTPException, status

UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The user with this email already exists in the system.",
)

InsufficientPrivilegesException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="The user doesn't have enough privileges",
)
