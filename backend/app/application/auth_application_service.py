"""Application layer orchestration for authentication use cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.auth_service import AuthService, auth_service
from app.models.user import User
from app.schemas.user import (
    AccessTokenResponse,
    AuthTokenResponse,
    UserPublicResponse,
    UserResponse,
)


class AuthApplicationService:
    """
    Application layer service for auth use cases.
    Converts domain results into response DTOs.
    """

    def __init__(self, auth_svc: AuthService = auth_service) -> None:
        self._auth_svc = auth_svc

    async def register(
        self,
        db: AsyncSession,
        *,
        username: str,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> AuthTokenResponse:
        user, access_token, refresh_token = await self._auth_svc.register(
            db,
            username=username,
            email=email,
            password=password,
            full_name=full_name,
        )
        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            user=self._to_public(user),
        )

    async def login(
        self, db: AsyncSession, *, email: str, password: str
    ) -> AuthTokenResponse:
        user, access_token, refresh_token = await self._auth_svc.authenticate(
            db, email=email, password=password
        )
        return AuthTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            user=self._to_public(user),
        )

    async def refresh(
        self, db: AsyncSession, *, refresh_token: str
    ) -> AccessTokenResponse:
        access_token = await self._auth_svc.refresh_access_token(
            db, refresh_token=refresh_token
        )
        return AccessTokenResponse(
            access_token=access_token,
            token_type="Bearer",
        )

    def get_current_user_response(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    @staticmethod
    def _to_public(user: User) -> UserPublicResponse:
        return UserPublicResponse(
            id=user.id,
            username=user.username,
            email=user.email,
        )


auth_application_service = AuthApplicationService()
