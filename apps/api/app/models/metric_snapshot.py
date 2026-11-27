
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    id = Column(BigInteger, primary_key=True, index=True)

    server_id = Column(
        Integer,
        ForeignKey("servers.id"),
        nullable=False,
        index=True,
    )

    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    disk_usage = Column(Float, nullable=False)

    network_bytes_sent = Column(BigInteger, default=0, nullable=False)
    network_bytes_received = Column(BigInteger, default=0, nullable=False)

    recorded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        Index(
            "ix_metric_snapshots_server_recorded",
            "server_id",
            "recorded_at",
        ),
    )

    server = relationship(
        "Server",
        back_populates="metric_snapshots",
    )
