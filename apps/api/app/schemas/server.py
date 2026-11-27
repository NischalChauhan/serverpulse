from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ServerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    hostname: str = Field(min_length=1, max_length=255)
    ip_address: str | None = Field(default=None, max_length=45)
    operating_system: str | None = Field(default=None, max_length=100)


class ServerResponse(BaseModel):
    id: int
    name: str
    hostname: str
    ip_address: str | None
    operating_system: str | None
    agent_status: str
    created_at: datetime
    last_seen_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
