"""JWT token creation and validation."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.config import settings


class TokenService:
    """Stateless JWT token management for access and refresh tokens."""

    def create_access_token(self, user_id: int) -> str:
        """Create a short-lived access token."""
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.now(UTC),
        }
        return jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    def create_refresh_token(self, user_id: int) -> str:
        """Create a long-lived refresh token."""
        expire = datetime.now(UTC) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(UTC),
        }
        return jwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token. Raises JWTError on failure."""
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            raise

    def decode_access_token(self, token: str) -> int:
        """Decode an access token and return the user_id. Raises JWTError on failure."""
        payload = self.decode_token(token)
        if payload.get("type") != "access":
            raise JWTError("Invalid token type: expected access token")
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise JWTError("Token missing subject claim")
        return int(user_id_str)

    def decode_refresh_token(self, token: str) -> int:
        """Decode a refresh token and return the user_id. Raises JWTError on failure."""
        payload = self.decode_token(token)
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type: expected refresh token")
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise JWTError("Token missing subject claim")
        return int(user_id_str)


token_service = TokenService()
