
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Server(Base):
    __tablename__ = "servers"

    __table_args__ = (
        UniqueConstraint(
            "agent_key_hash",
            name="uq_servers_agent_key_hash",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(45), nullable=True)

    operating_system = Column(String(100), nullable=True)

    agent_status = Column(
        String(20),
        nullable=False,
        default="offline",
    )

    agent_key_hash = Column(
        String(64),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    last_seen_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    metric_snapshots = relationship(
        "MetricSnapshot",
        back_populates="server",
        cascade="all, delete-orphan",
    )

    alerts = relationship(
        "Alert",
        back_populates="server",
    )
