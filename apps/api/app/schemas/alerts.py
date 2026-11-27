
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# --------------------------------------------------
# ALERT RULE SCHEMAS
# --------------------------------------------------

class AlertRuleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    metric_name: str = Field(min_length=1, max_length=50)
    operator: str = Field(pattern=r"^(gt|lt|gte|lte)$")
    threshold: float = Field(ge=0)
    severity: str = Field(default="warning", pattern=r"^(warning|critical)$")


class AlertRuleResponse(BaseModel):
    id: int
    name: str
    metric_name: str
    operator: str
    threshold: float
    severity: str
    is_enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# ALERT RESPONSE SCHEMA
# --------------------------------------------------

class AlertResponse(BaseModel):
    id: int
    server_id: int
    rule_id: int | None
    metric_name: str
    current_value: float
    threshold: float
    severity: str
    status: str
    message: str
    created_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
