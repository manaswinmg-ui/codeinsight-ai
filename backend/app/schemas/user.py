from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None


class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    updated_at: datetime
    is_superuser: bool


# Additional properties to return via API
class UserResponse(UserInDBBase):
    pass


# ─── Auth Request / Response Schemas ──────────────────────────────────


class UserRegisterRequest(BaseModel):
    """Registration request payload."""

    username: str = Field(
        ..., min_length=3, max_length=150, pattern=r"^[a-zA-Z0-9_-]+$"
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = None


class UserLoginRequest(BaseModel):
    """Login request payload."""

    email: EmailStr
    password: str


class UserPublicResponse(BaseModel):
    """Minimal user info returned inside auth token responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


class AuthTokenResponse(BaseModel):
    """Response containing access and refresh tokens after login/register."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    user: UserPublicResponse


class AccessTokenResponse(BaseModel):
    """Response containing a refreshed access token."""

    access_token: str
    token_type: str = "Bearer"


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token."""

    refresh_token: str
