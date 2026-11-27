
from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.user import User


def require_roles(*allowed_roles: str):

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        user_role = current_user.role.name

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return role_checker


# Full administrative access
require_admin = require_roles("admin")


# Administrative and operational access
require_operator = require_roles("admin", "operator")


# Any authenticated role
require_authenticated = require_roles(
    "admin",
    "operator",
    "viewer",
)
