"""FastAPI dependencies for authentication."""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import TokenService, token_service
from app.db import get_db
from app.models.user import User
from app.repositories.user import UserRepository, user_repository

logger = logging.getLogger("app.auth.dependencies")

# HTTPBearer extracts the token from "Authorization: Bearer <token>" header.
# auto_error=True means it raises 403 if no header is present (used for mandatory auth).
# auto_error=False means it returns None if no header is present (used for optional auth).
_bearer_scheme = HTTPBearer(auto_error=True)
_bearer_scheme_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
    ts: TokenService = Depends(lambda: token_service),
    user_repo: UserRepository = Depends(lambda: user_repository),
) -> User:
    """
    Mandatory authentication dependency.
    Extracts and validates the JWT access token, then loads the User.
    Raises 401 if the token is missing, invalid, expired, or the user is inactive.
    """
    try:
        user_id = ts.decode_access_token(credentials.credentials)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await user_repo.get(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    return user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme_optional),
    db: AsyncSession = Depends(get_db),
    ts: TokenService = Depends(lambda: token_service),
    user_repo: UserRepository = Depends(lambda: user_repository),
) -> User | None:
    """
    Optional authentication dependency.
    Returns the User if a valid Bearer token is present, or None otherwise.
    Used for endpoints that work for both authenticated and anonymous users.
    """
    if credentials is None:
        return None

    try:
        user_id = ts.decode_access_token(credentials.credentials)
    except JWTError:
        # Token is present but invalid — silently return None for optional auth
        return None

    user = await user_repo.get(db, user_id)
    if user is None or not user.is_active:
        return None
    return user
