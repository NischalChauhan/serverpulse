
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.permissions import (
    require_admin,
    require_operator,
    require_authenticated,
)
from app.db.session import get_db
from app.models.alert import Alert
from app.models.alert_rule import AlertRule
from app.models.user import User
from app.schemas.alerts import (
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
)
from app.services.audit_service import log_action


router = APIRouter(
    prefix="/alerts",
    tags=["Alert Management"],
)


def get_request_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


# ==========================================
# LIST ALERTS
# Admin, Operator, Viewer
# ==========================================

@router.get(
    "",
    response_model=list[AlertResponse],
)
def list_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    return (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .all()
    )


# ==========================================
# CREATE ALERT RULE
# Admin only
# ==========================================

@router.post(
    "/rules",
    response_model=AlertRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_alert_rule(
    rule_data: AlertRuleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    new_rule = AlertRule(
        name=rule_data.name,
        metric_name=rule_data.metric_name,
        operator=rule_data.operator,
        threshold=rule_data.threshold,
        severity=rule_data.severity,
        is_enabled=True,
    )

    try:
        db.add(new_rule)
        db.flush()

        log_action(
            db,
            action="alert_rule.create",
            user_id=current_user.id,
            resource_type="alert_rule",
            resource_id=new_rule.id,
            details={
                "name": new_rule.name,
                "metric_name": new_rule.metric_name,
                "operator": new_rule.operator,
                "threshold": new_rule.threshold,
                "severity": new_rule.severity,
            },
            ip_address=get_request_ip(request),
        )

        db.commit()
        db.refresh(new_rule)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create alert rule",
        )

    return new_rule


# ==========================================
# LIST ALERT RULES
# Admin, Operator, Viewer
# ==========================================

@router.get(
    "/rules",
    response_model=list[AlertRuleResponse],
)
def list_alert_rules(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    return (
        db.query(AlertRule)
        .order_by(AlertRule.id.asc())
        .all()
    )


# ==========================================
# ACKNOWLEDGE ALERT
# Admin, Operator
# ==========================================

@router.patch(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
)
def acknowledge_alert(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    if alert.status != "open":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only open alerts can be acknowledged",
        )

    alert.status = "acknowledged"
    alert.acknowledged_at = datetime.now(timezone.utc)

    try:
        log_action(
            db,
            action="alert.acknowledge",
            user_id=current_user.id,
            resource_type="alert",
            resource_id=alert.id,
            details={
                "server_id": alert.server_id,
                "metric_name": alert.metric_name,
                "severity": alert.severity,
            },
            ip_address=get_request_ip(request),
        )

        db.commit()
        db.refresh(alert)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to acknowledge alert",
        )

    return alert


# ==========================================
# RESOLVE ALERT
# Admin, Operator
# ==========================================

@router.patch(
    "/{alert_id}/resolve",
    response_model=AlertResponse,
)
def resolve_alert(
    alert_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator),
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    if alert.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alert is already resolved",
        )

    alert.status = "resolved"
    alert.resolved_at = datetime.now(timezone.utc)

    try:
        log_action(
            db,
            action="alert.resolve",
            user_id=current_user.id,
            resource_type="alert",
            resource_id=alert.id,
            details={
                "server_id": alert.server_id,
                "metric_name": alert.metric_name,
                "severity": alert.severity,
            },
            ip_address=get_request_ip(request),
        )

        db.commit()
        db.refresh(alert)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to resolve alert",
        )

    return alert
