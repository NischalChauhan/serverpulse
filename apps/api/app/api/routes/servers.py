
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.agent_security import generate_agent_key, hash_agent_key
from app.core.permissions import require_admin, require_authenticated
from app.db.session import get_db
from app.models.server import Server
from app.models.user import User
from app.schemas.server import ServerCreate, ServerResponse
from app.services.audit_service import log_action


router = APIRouter(
    prefix="/servers",
    tags=["Server Inventory"],
)


def get_request_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


# ==========================================
# REGISTER SERVER
# ==========================================

@router.post(
    "",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_server(
    server_data: ServerCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    existing_server = (
        db.query(Server)
        .filter(Server.hostname == server_data.hostname)
        .first()
    )

    if existing_server:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Server hostname already registered",
        )

    new_server = Server(
        name=server_data.name,
        hostname=server_data.hostname,
        ip_address=server_data.ip_address,
        operating_system=server_data.operating_system,
        agent_status="offline",
    )

    try:
        db.add(new_server)
        db.flush()

        log_action(
            db,
            action="server.register",
            user_id=current_user.id,
            resource_type="server",
            resource_id=new_server.id,
            details={
                "name": new_server.name,
                "hostname": new_server.hostname,
            },
            ip_address=get_request_ip(request),
        )

        db.commit()
        db.refresh(new_server)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Server registration conflict",
        )

    return new_server


# ==========================================
# LIST SERVERS
# ==========================================

@router.get(
    "",
    response_model=list[ServerResponse],
)
def list_servers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_authenticated),
):
    return (
        db.query(Server)
        .order_by(Server.id.asc())
        .all()
    )


# ==========================================
# GENERATE / ROTATE AGENT KEY
# ==========================================

@router.post(
    "/{server_id}/agent-key",
    status_code=status.HTTP_201_CREATED,
)
def provision_agent_key(
    server_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    server = (
        db.query(Server)
        .filter(Server.id == server_id)
        .first()
    )

    if server is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server not found",
        )

    is_rotation = server.agent_key_hash is not None

    agent_key = generate_agent_key()

    server.agent_key_hash = hash_agent_key(agent_key)

    log_action(
        db,
        action=(
            "server.agent_key_rotated"
            if is_rotation
            else "server.agent_key_generated"
        ),
        user_id=current_user.id,
        resource_type="server",
        resource_id=server.id,
        details={
            "hostname": server.hostname,
        },
        ip_address=get_request_ip(request),
    )

    db.commit()

    return {
        "message": (
            "Agent key rotated successfully"
            if is_rotation
            else "Agent key generated successfully"
        ),
        "server_id": server.id,
        "agent_key": agent_key,
        "warning": "Store this key securely. It cannot be retrieved again.",
    }
