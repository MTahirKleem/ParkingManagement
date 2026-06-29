from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class User(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: ObjectId | None = Field(default=None, alias="_id")
    name: str
    email: EmailStr
    phone: str | None = None
    password_hash: str
    role: str
    status: str
    last_login_at: datetime | None = None
    created_by: ObjectId | None = None
    updated_by: ObjectId | None = None
    created_at: datetime
    updated_at: datetime

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=False)
