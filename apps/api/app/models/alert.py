
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=True)

    metric_name = Column(String(50), nullable=False)
    current_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)

    severity = Column(String(20), nullable=False, default="warning")
    status = Column(String(20), nullable=False, default="open")

    message = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    server = relationship(
        "Server",
        back_populates="alerts",
    )

    rule = relationship(
        "AlertRule",
        back_populates="alerts",
    )
