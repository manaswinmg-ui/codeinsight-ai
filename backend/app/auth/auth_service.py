"""Authentication domain service — registration, login, and token refresh."""

import logging

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import TokenService, token_service
from app.auth.password import PasswordService, password_service
from app.models.user import User
from app.repositories.user import UserRepository, user_repository

logger = logging.getLogger("app.auth.auth_service")


class DuplicateEmailError(Exception):
    """Raised when a user tries to register with an already-used email."""


class DuplicateUsernameError(Exception):
    """Raised when a user tries to register with an already-used username."""


class InvalidCredentialsError(Exception):
    """Raised when email/password combination is incorrect."""


class InactiveUserError(Exception):
    """Raised when an inactive user tries to log in."""


class InvalidRefreshTokenError(Exception):
    """Raised when a refresh token is invalid or expired."""


class AuthService:
    """Domain service coordinating user registration, authentication, and token refresh."""

    def __init__(
        self,
        user_repo: UserRepository = user_repository,
        pwd_svc: PasswordService = password_service,
        tkn_svc: TokenService = token_service,
    ) -> None:
        self._user_repo = user_repo
        self._pwd_svc = pwd_svc
        self._tkn_svc = tkn_svc

    async def register(
        self,
        db: AsyncSession,
        *,
        username: str,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> tuple[User, str, str]:
        """
        Register a new user.
        Returns (user, access_token, refresh_token).
        Raises DuplicateEmailError or DuplicateUsernameError on conflict.
        """
        # Check uniqueness
        existing_email = await self._user_repo.get_by_email(db, email)
        if existing_email:
            raise DuplicateEmailError(f"Email '{email}' is already registered")

        existing_username = await self._user_repo.get_by_username(db, username)
        if existing_username:
            raise DuplicateUsernameError(f"Username '{username}' is already taken")

        # Hash password and create user
        hashed_password = self._pwd_svc.hash_password(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Generate tokens
        access_token = self._tkn_svc.create_access_token(user.id)
        refresh_token = self._tkn_svc.create_refresh_token(user.id)

        logger.info("User registered: id=%s, username=%s", user.id, user.username)
        return user, access_token, refresh_token

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> tuple[User, str, str]:
        """
        Authenticate a user with email and password.
        Returns (user, access_token, refresh_token).
        Raises InvalidCredentialsError or InactiveUserError.
        """
        user = await self._user_repo.get_by_email(db, email)
        if user is None:
            # Generic error to prevent user enumeration
            raise InvalidCredentialsError("Invalid email or password")

        if not user.is_active:
            raise InactiveUserError("User account is inactive")

        if not self._pwd_svc.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        # Generate tokens
        access_token = self._tkn_svc.create_access_token(user.id)
        refresh_token = self._tkn_svc.create_refresh_token(user.id)

        logger.info("User authenticated: id=%s, username=%s", user.id, user.username)
        return user, access_token, refresh_token

    async def refresh_access_token(
        self, db: AsyncSession, *, refresh_token: str
    ) -> str:
        """
        Generate a new access token from a valid refresh token.
        Returns the new access_token string.
        Raises InvalidRefreshTokenError.
        """
        try:
            user_id = self._tkn_svc.decode_refresh_token(refresh_token)
        except JWTError as exc:
            raise InvalidRefreshTokenError(
                "Invalid or expired refresh token"
            ) from exc

        user = await self._user_repo.get(db, user_id)
        if user is None or not user.is_active:
            raise InvalidRefreshTokenError("User not found or inactive")

        access_token = self._tkn_svc.create_access_token(user.id)
        logger.info("Access token refreshed for user id=%s", user.id)
        return access_token


auth_service = AuthService()
