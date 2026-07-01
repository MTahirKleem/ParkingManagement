from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


class AuditLog(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: ObjectId | None = Field(default=None, alias="_id")
    user_id: ObjectId | None = None
    user_role: str | None = None
    action: str
    entity: str
    entity_id: ObjectId | None = None
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

    def to_mongo(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude={"id"})
