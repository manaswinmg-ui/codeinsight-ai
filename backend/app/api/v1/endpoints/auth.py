"""Authentication API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth_application_service import (
    AuthApplicationService,
    auth_application_service,
)
from app.auth.auth_service import (
    DuplicateEmailError,
    DuplicateUsernameError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.auth.dependencies import get_current_user
from app.db import get_db
from app.models.user import User
from app.schemas.user import (
    AccessTokenResponse,
    AuthTokenResponse,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter()
logger = logging.getLogger("app.api.auth")


@router.post(
    "/register",
    response_model=AuthTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
    app_service: AuthApplicationService = Depends(
        lambda: auth_application_service
    ),
) -> AuthTokenResponse:
    """Create a new user and return JWT tokens."""
    try:
        return await app_service.register(
            db,
            username=payload.username,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
        )
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except DuplicateUsernameError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error during registration: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from exc


@router.post(
    "/login",
    response_model=AuthTokenResponse,
    summary="Authenticate and obtain JWT tokens",
)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
    app_service: AuthApplicationService = Depends(
        lambda: auth_application_service
    ),
) -> AuthTokenResponse:
    """Authenticate with email and password, returning JWT tokens."""
    try:
        return await app_service.login(
            db, email=payload.email, password=payload.password
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error during login: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from exc


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh an expired access token",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    app_service: AuthApplicationService = Depends(
        lambda: auth_application_service
    ),
) -> AccessTokenResponse:
    """Generate a new access token from a valid refresh token."""
    try:
        return await app_service.refresh(db, refresh_token=payload.refresh_token)
    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error during token refresh: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        ) from exc


@router.post(
    "/logout",
    summary="Log out the current user",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Log out the current user.
    Since JWTs are stateless, this is a no-op on the server side.
    The client should discard the stored tokens.
    """
    logger.info("User logged out: id=%d, username=%s", current_user.id, current_user.username)
    return {"message": "Successfully logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
async def get_me(
    current_user: User = Depends(get_current_user),
    app_service: AuthApplicationService = Depends(
        lambda: auth_application_service
    ),
) -> UserResponse:
    """Return profile information for the authenticated user."""
    return app_service.get_current_user_response(current_user)
