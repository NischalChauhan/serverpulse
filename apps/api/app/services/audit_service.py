
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    *,
    action: str,
    user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """
    Add an audit record to the current database transaction.

    The caller is responsible for committing or rolling back.
    Never include passwords, JWTs, API keys, or other secrets
    in the audit details.
    """

    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=(
            str(resource_id) if resource_id is not None else None
        ),
        details=details,
        ip_address=ip_address,
    )

    db.add(audit_entry)

    return audit_entry
