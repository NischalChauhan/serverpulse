
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.db.session import get_db
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.services.audit_service import log_action

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_request_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


# ==========================================
# USER REGISTRATION
# ==========================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    viewer_role = (
        db.query(Role)
        .filter(Role.name == "viewer")
        .first()
    )

    if not viewer_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default viewer role is not configured",
        )

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hash_password(user_data.password),
        role_id=viewer_role.id,
    )

    try:
        db.add(new_user)
        db.flush()

        log_action(
            db,
            action="auth.register_success",
            user_id=new_user.id,
            resource_type="user",
            resource_id=new_user.id,
            details={
                "email": new_user.email,
                "role": "viewer",
            },
            ip_address=get_request_ip(request),
        )

        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    return new_user


# ==========================================
# USER LOGIN
# ==========================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user or not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        log_action(
            db,
            action="auth.login_failed",
            user_id=user.id if user else None,
            resource_type="user",
            details={
                "email": user_data.email,
                "reason": "invalid_credentials",
            },
            ip_address=get_request_ip(request),
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        log_action(
            db,
            action="auth.login_failed",
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            details={
                "reason": "inactive_account",
            },
            ip_address=get_request_ip(request),
        )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        subject=str(user.id)
    )

    log_action(
        db,
        action="auth.login_success",
        user_id=user.id,
        resource_type="user",
        resource_id=user.id,
        details={
            "email": user.email,
        },
        ip_address=get_request_ip(request),
    )

    db.commit()

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


# ==========================================
# CURRENT AUTHENTICATED USER
# ==========================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user
