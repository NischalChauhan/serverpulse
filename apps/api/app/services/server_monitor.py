
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.server import Server


OFFLINE_THRESHOLD_SECONDS = 60


def update_server_statuses(db: Session) -> int:
    """
    Mark servers offline if they have not sent metrics
    within the configured heartbeat threshold.

    Returns the number of servers marked offline.
    """

    current_time = datetime.now(timezone.utc)

    cutoff_time = current_time - timedelta(
        seconds=OFFLINE_THRESHOLD_SECONDS
    )

    stale_servers = (
        db.query(Server)
        .filter(
            Server.agent_status == "online",
            (
                (Server.last_seen_at.is_(None))
                | (Server.last_seen_at < cutoff_time)
            ),
        )
        .all()
    )

    for server in stale_servers:
        server.agent_status = "offline"

    if stale_servers:
        db.commit()

    return len(stale_servers)
