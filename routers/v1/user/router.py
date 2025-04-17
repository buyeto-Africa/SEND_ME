# routers/v1/user/router.py
from fastapi import APIRouter, Depends
from core.deps import get_current_active_user, RoleChecker
from models.user import User

# Create the router
router = APIRouter(tags=["Users"])

# Role-based access control
allow_customer = RoleChecker(["customer"])
allow_tenant_admin = RoleChecker(["tenant_admin"])
allow_platform_admin = RoleChecker(["platform_admin"])
allow_admin = RoleChecker(["tenant_admin", "platform_admin"])

@router.get("/users/me", summary="Get current user information")
async def get_user_me(current_user: User = Depends(get_current_active_user)):
    """
    Get information about the currently authenticated user.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "tenant_id": current_user.tenant_id,
        "role": current_user.role
    }

@router.get("/users/admin", summary="Admin only endpoint")
async def admin_only(current_user: User = Depends(allow_admin)):
    """
    This endpoint is only accessible to users with admin roles
    """
    return {"message": "You have admin access", "user_id": current_user.id}

@router.get("/users/customer", summary="Customer only endpoint")
async def customer_only(current_user: User = Depends(allow_customer)):
    """
    This endpoint is only accessible to customers
    """
    return {"message": "You have customer access", "user_id": current_user.id}