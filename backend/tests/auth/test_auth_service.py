from unittest.mock import AsyncMock, MagicMock

import pytest

from app.auth.auth_service import (
    AuthService,
    DuplicateEmailError,
    DuplicateUsernameError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.models.user import User


@pytest.mark.asyncio
async def test_register_success() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    # User doesn't exist yet
    user_repo.get_by_email = AsyncMock(return_value=None)
    user_repo.get_by_username = AsyncMock(return_value=None)

    pwd_svc.hash_password.return_value = "hashed_pass"
    tkn_svc.create_access_token.return_value = "access_val"
    tkn_svc.create_refresh_token.return_value = "refresh_val"

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    user, access, refresh = await auth_svc.register(
        db,
        username="new_user",
        email="new@example.com",
        password="password123",
        full_name="New User",
    )

    assert user.username == "new_user"
    assert user.email == "new@example.com"
    assert user.hashed_password == "hashed_pass"
    assert access == "access_val"
    assert refresh == "refresh_val"

    # Verifications
    user_repo.get_by_email.assert_called_once_with(db, "new@example.com")
    user_repo.get_by_username.assert_called_once_with(db, "new_user")
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    existing_user = User(id=1, email="dup@example.com", username="user1")
    user_repo.get_by_email = AsyncMock(return_value=existing_user)
    user_repo.get_by_username = AsyncMock(return_value=None)

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    with pytest.raises(DuplicateEmailError):
        await auth_svc.register(
            db, username="user2", email="dup@example.com", password="password"
        )


@pytest.mark.asyncio
async def test_register_duplicate_username() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    existing_user = User(id=1, email="user1@example.com", username="dup")
    user_repo.get_by_email = AsyncMock(return_value=None)
    user_repo.get_by_username = AsyncMock(return_value=existing_user)

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    with pytest.raises(DuplicateUsernameError):
        await auth_svc.register(
            db, username="dup", email="user2@example.com", password="password"
        )


@pytest.mark.asyncio
async def test_authenticate_success() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    user = User(
        id=42,
        username="user1",
        email="user1@example.com",
        hashed_password="hashed_pass",
        is_active=True,
    )
    user_repo.get_by_email = AsyncMock(return_value=user)
    pwd_svc.verify_password.return_value = True
    tkn_svc.create_access_token.return_value = "access"
    tkn_svc.create_refresh_token.return_value = "refresh"

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    authed_user, access, refresh = await auth_svc.authenticate(
        db, email="user1@example.com", password="password"
    )

    assert authed_user == user
    assert access == "access"
    assert refresh == "refresh"


@pytest.mark.asyncio
async def test_authenticate_invalid_email() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    user_repo.get_by_email = AsyncMock(return_value=None)

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    with pytest.raises(InvalidCredentialsError):
        await auth_svc.authenticate(
            db, email="wrong@example.com", password="password"
        )


@pytest.mark.asyncio
async def test_authenticate_wrong_password() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    user = User(id=1, email="user@example.com", username="user1", hashed_password="hashed", is_active=True)
    user_repo.get_by_email = AsyncMock(return_value=user)
    pwd_svc.verify_password.return_value = False

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    with pytest.raises(InvalidCredentialsError):
        await auth_svc.authenticate(
            db, email="user@example.com", password="wrong"
        )


@pytest.mark.asyncio
async def test_authenticate_inactive_user() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    user = User(id=1, email="inactive@example.com", username="user1", is_active=False)
    user_repo.get_by_email = AsyncMock(return_value=user)

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    with pytest.raises(InactiveUserError):
        await auth_svc.authenticate(
            db, email="inactive@example.com", password="password"
        )


@pytest.mark.asyncio
async def test_refresh_token_success() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    user = User(id=5, email="user@example.com", username="user1", is_active=True)
    tkn_svc.decode_refresh_token.return_value = 5
    user_repo.get = AsyncMock(return_value=user)
    tkn_svc.create_access_token.return_value = "new_access_token"

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    new_access = await auth_svc.refresh_access_token(db, refresh_token="old_refresh")

    assert new_access == "new_access_token"
    tkn_svc.decode_refresh_token.assert_called_once_with("old_refresh")
    user_repo.get.assert_called_once_with(db, 5)
    tkn_svc.create_access_token.assert_called_once_with(5)


@pytest.mark.asyncio
async def test_refresh_token_invalid() -> None:
    db = AsyncMock()
    user_repo = MagicMock()
    pwd_svc = MagicMock()
    tkn_svc = MagicMock()

    from jose import JWTError
    tkn_svc.decode_refresh_token.side_effect = JWTError("Invalid token")

    auth_svc = AuthService(user_repo=user_repo, pwd_svc=pwd_svc, tkn_svc=tkn_svc)
    with pytest.raises(InvalidRefreshTokenError):
        await auth_svc.refresh_access_token(db, refresh_token="bad_token")
