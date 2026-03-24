from fastapi import HTTPException, status

CredentialsException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Could not validate credentials",
)

InactiveUserException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Inactive user",
)

InvalidTokenException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid token",
)
