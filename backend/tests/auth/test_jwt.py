from datetime import UTC, datetime, timedelta

import pytest
from jose import JWTError, jwt

from app.auth.jwt import token_service
from app.config import settings


def test_create_access_token() -> None:
    user_id = 42
    token = token_service.create_access_token(user_id)

    decoded = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["sub"] == str(user_id)
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_refresh_token() -> None:
    user_id = 42
    token = token_service.create_refresh_token(user_id)

    decoded = jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert decoded["sub"] == str(user_id)
    assert decoded["type"] == "refresh"
    assert "exp" in decoded


def test_decode_valid_tokens() -> None:
    user_id = 99
    access_token = token_service.create_access_token(user_id)
    refresh_token = token_service.create_refresh_token(user_id)

    assert token_service.decode_access_token(access_token) == user_id
    assert token_service.decode_refresh_token(refresh_token) == user_id


def test_decode_invalid_type_raises_error() -> None:
    user_id = 99
    access_token = token_service.create_access_token(user_id)
    refresh_token = token_service.create_refresh_token(user_id)

    with pytest.raises(JWTError):
        token_service.decode_access_token(refresh_token)

    with pytest.raises(JWTError):
        token_service.decode_refresh_token(access_token)


def test_decode_expired_token_raises_error() -> None:
    # Create an expired token manually
    expire = datetime.now(UTC) - timedelta(minutes=5)
    payload = {"sub": "100", "type": "access", "exp": expire}
    expired_token = jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    with pytest.raises(JWTError):
        token_service.decode_access_token(expired_token)
