
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.alert_rule import AlertRule
from app.models.metric_snapshot import MetricSnapshot
from app.services.audit_service import log_action


METRIC_FIELDS = {
    "cpu_usage": "cpu_usage",
    "memory_usage": "memory_usage",
    "disk_usage": "disk_usage",
}


def evaluate_condition(
    current_value: float,
    operator: str,
    threshold: float,
) -> bool:
    if operator == "gt":
        return current_value > threshold

    if operator == "lt":
        return current_value < threshold

    if operator == "gte":
        return current_value >= threshold

    if operator == "lte":
        return current_value <= threshold

    return False


def evaluate_alert_rules(
    db: Session,
    snapshot: MetricSnapshot,
) -> None:
    """
    Evaluate enabled alert rules against a new metric snapshot.

    Existing open or acknowledged alerts are not duplicated.
    Resolved alerts can be generated again if the condition
    is triggered in a later monitoring cycle.

    Audit records are added to the same transaction.
    The caller is responsible for committing or rolling back.
    """

    rules = (
        db.query(AlertRule)
        .filter(AlertRule.is_enabled.is_(True))
        .all()
    )

    for rule in rules:
        field_name = METRIC_FIELDS.get(rule.metric_name)

        # Ignore unsupported metric names.
        if field_name is None:
            continue

        current_value = getattr(snapshot, field_name)

        triggered = evaluate_condition(
            current_value=current_value,
            operator=rule.operator,
            threshold=rule.threshold,
        )

        existing_alert = (
            db.query(Alert)
            .filter(
                Alert.server_id == snapshot.server_id,
                Alert.rule_id == rule.id,
                Alert.status.in_(["open", "acknowledged"]),
            )
            .first()
        )

        if triggered:
            if existing_alert is not None:
                # Avoid creating duplicate active alerts.
                continue

            alert = Alert(
                server_id=snapshot.server_id,
                rule_id=rule.id,
                metric_name=rule.metric_name,
                current_value=current_value,
                threshold=rule.threshold,
                severity=rule.severity,
                status="open",
                message=(
                    f"{rule.name}: {rule.metric_name} "
                    f"is {current_value:.2f}; "
                    f"threshold is {rule.operator} "
                    f"{rule.threshold:.2f}"
                ),
            )

            db.add(alert)
            db.flush()

            log_action(
                db,
                action="alert.auto_create",
                resource_type="alert",
                resource_id=alert.id,
                details={
                    "server_id": snapshot.server_id,
                    "rule_id": rule.id,
                    "metric_name": rule.metric_name,
                    "current_value": current_value,
                    "threshold": rule.threshold,
                    "severity": rule.severity,
                },
            )

        elif existing_alert is not None:
            # Automatically resolve an active alert when
            # its triggering condition is no longer true.

            existing_alert.status = "resolved"
            existing_alert.resolved_at = datetime.now(timezone.utc)

            log_action(
                db,
                action="alert.auto_resolve",
                resource_type="alert",
                resource_id=existing_alert.id,
                details={
                    "server_id": snapshot.server_id,
                    "rule_id": rule.id,
                    "metric_name": rule.metric_name,
                    "current_value": current_value,
                    "threshold": rule.threshold,
                },
            )
