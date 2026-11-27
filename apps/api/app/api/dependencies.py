
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.agent_security import hash_agent_key
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.server import Server
from app.models.user import User


# Separate authentication schemes
bearer_scheme = HTTPBearer(auto_error=False)
agent_bearer_scheme = HTTPBearer(auto_error=False)


# ==========================================
# DASHBOARD USER AUTHENTICATION
# ==========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


# ==========================================
# MONITORING AGENT AUTHENTICATION
# ==========================================

def get_current_agent(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        agent_bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> Server:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    agent_key = credentials.credentials

    agent_key_hash = hash_agent_key(agent_key)

    server = (
        db.query(Server)
        .filter(Server.agent_key_hash == agent_key_hash)
        .first()
    )

    if server is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return server
