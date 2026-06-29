from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.constants import UserRoles, UserStatus


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class AuthUserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: Literal[UserRoles.ADMIN, UserRoles.GUARD]
    status: Literal[
        UserStatus.ACTIVE,
        UserStatus.INACTIVE,
        UserStatus.DELETED,
    ]


class LoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse


class RefreshTokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
