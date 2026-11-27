
from fastapi import APIRouter, Depends

from app.core.permissions import (
    require_admin,
    require_operator,
    require_authenticated,
)
from app.models.user import User

router = APIRouter(
    prefix="/permissions",
    tags=["Role-Based Access Control"],
)


@router.get("/viewer")
def viewer_access(
    current_user: User = Depends(require_authenticated),
):
    return {
        "message": "Authenticated access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }


@router.get("/operator")
def operator_access(
    current_user: User = Depends(require_operator),
):
    return {
        "message": "Operator access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }


@router.get("/admin")
def admin_access(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Administrator access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }
