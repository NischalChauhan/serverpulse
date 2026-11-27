
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_agent, get_current_user
from app.db.session import get_db
from app.models.metric_snapshot import MetricSnapshot
from app.models.server import Server
from app.schemas.metrics import (
    MetricSnapshotCreate,
    MetricSnapshotResponse,
)
from app.services.alert_engine import evaluate_alert_rules


router = APIRouter(
    prefix="/metrics",
    tags=["System Metrics"],
)


# --------------------------------------------------
# AGENT METRICS INGESTION + AUTOMATIC ALERT EVALUATION
# --------------------------------------------------

@router.post(
    "/ingest",
    response_model=MetricSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def ingest_metrics(
    metric_data: MetricSnapshotCreate,
    db: Session = Depends(get_db),
    current_server: Server = Depends(get_current_agent),
):
    if metric_data.server_id != current_server.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent cannot submit metrics for another server",
        )

    current_time = datetime.now(timezone.utc)

    snapshot = MetricSnapshot(
        server_id=current_server.id,
        cpu_usage=metric_data.cpu_usage,
        memory_usage=metric_data.memory_usage,
        disk_usage=metric_data.disk_usage,
        network_bytes_sent=metric_data.network_bytes_sent,
        network_bytes_received=metric_data.network_bytes_received,
        recorded_at=current_time,
    )

    try:
        db.add(snapshot)
        db.flush()

        # Evaluate enabled alert rules using this snapshot.
        evaluate_alert_rules(db, snapshot)

        current_server.agent_status = "online"
        current_server.last_seen_at = current_time

        # Save metrics and alert changes together.
        db.commit()
        db.refresh(snapshot)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to store metrics or evaluate alert rules",
        )

    return snapshot


# --------------------------------------------------
# LATEST METRICS FOR ALL SERVERS
# --------------------------------------------------

@router.get(
    "/latest",
    response_model=list[MetricSnapshotResponse],
)
def get_latest_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    latest_snapshots = (
        db.query(MetricSnapshot)
        .from_statement(
            db.query(MetricSnapshot)
            .filter(
                MetricSnapshot.id.in_(
                    db.query(MetricSnapshot.id)
                    .distinct(MetricSnapshot.server_id)
                    .order_by(
                        MetricSnapshot.server_id,
                        MetricSnapshot.recorded_at.desc(),
                    )
                )
            )
            .statement
        )
        .all()
    )

    return latest_snapshots


# --------------------------------------------------
# LATEST METRICS FOR ONE SERVER
# --------------------------------------------------

@router.get(
    "/{server_id}/latest",
    response_model=MetricSnapshotResponse,
)
def get_server_latest_metrics(
    server_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    server = db.query(Server).filter(
        Server.id == server_id
    ).first()

    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )

    snapshot = (
        db.query(MetricSnapshot)
        .filter(MetricSnapshot.server_id == server_id)
        .order_by(MetricSnapshot.recorded_at.desc())
        .first()
    )

    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics available for this server",
        )

    return snapshot


# --------------------------------------------------
# HISTORICAL METRICS FOR ONE SERVER
# --------------------------------------------------

@router.get(
    "/{server_id}/history",
    response_model=list[MetricSnapshotResponse],
)
def get_server_metrics_history(
    server_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    server = db.query(Server).filter(
        Server.id == server_id
    ).first()

    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )

    snapshots = (
        db.query(MetricSnapshot)
        .filter(MetricSnapshot.server_id == server_id)
        .order_by(MetricSnapshot.recorded_at.desc())
        .limit(limit)
        .all()
    )

    return snapshots
