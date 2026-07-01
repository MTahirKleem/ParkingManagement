from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.core.constants import UserRoles, UserStatus


class UserCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1)
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)
    role: Literal[UserRoles.GUARD]

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    phone: str | None = None
    status: Literal[
        UserStatus.ACTIVE,
        UserStatus.INACTIVE,
        UserStatus.DELETED,
    ] | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "UserUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one update field is required")
        return self


class PasswordResetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    new_password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str | None = None
    role: Literal[UserRoles.ADMIN, UserRoles.GUARD]
    status: Literal[
        UserStatus.ACTIVE,
        UserStatus.INACTIVE,
        UserStatus.DELETED,
    ]
    last_login_at: datetime | None = None
    created_by: str | None = None
    updated_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DeletedUserResponse(BaseModel):
    id: str
    status: Literal[UserStatus.DELETED]


class PasswordResetResponse(BaseModel):
    id: str
