from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MetricSnapshotCreate(BaseModel):
    server_id: int = Field(gt=0)

    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    disk_usage: float = Field(ge=0, le=100)

    network_bytes_sent: int = Field(ge=0)
    network_bytes_received: int = Field(ge=0)

    model_config = ConfigDict(extra="forbid")


class MetricSnapshotResponse(BaseModel):
    id: int
    server_id: int

    cpu_usage: float
    memory_usage: float
    disk_usage: float

    network_bytes_sent: int
    network_bytes_received: int

    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
