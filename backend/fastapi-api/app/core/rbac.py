from fastapi import Depends, Header
from typing import List, Optional
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.database import get_db_cursor

def get_token_from_header(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise UnauthorizedError("Missing Authorization header")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError("Invalid Authorization header format. Expected 'Bearer <token>'")
    return parts[1]

def get_current_user(token: str = Depends(get_token_from_header)) -> dict:
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedError("Invalid, malformed or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Token payload missing subject")
    
    with get_db_cursor() as cur:
        cur.execute("""
            SELECT u.user_id, u.email, u.full_name, u.phone, u.is_active
            FROM users u
            WHERE u.user_id = %s;
        """, (user_id,))
        user = cur.fetchone()
        
        if not user:
            raise UnauthorizedError("User account no longer exists")
        if not user["is_active"]:
            raise UnauthorizedError("User account is deactivated")
        
        # Fetch user roles
        cur.execute("""
            SELECT r.role_id, r.role_name
            FROM roles r
            JOIN user_roles ur ON r.role_id = ur.role_id
            WHERE ur.user_id = %s;
        """, (user_id,))
        role_rows = cur.fetchall()
        roles = [r["role_name"] for r in role_rows]
        user["roles"] = roles
        
        # Fetch user permissions
        cur.execute("""
            SELECT DISTINCT p.permission_code
            FROM permissions p
            JOIN role_permissions rp ON p.permission_id = rp.permission_id
            JOIN user_roles ur ON rp.role_id = ur.role_id
            WHERE ur.user_id = %s;
        """, (user_id,))
        perm_rows = cur.fetchall()
        user["permissions"] = [p["permission_code"] for p in perm_rows]
        
    return user

def require_roles(*allowed_roles: str):
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = current_user.get("roles", [])
        # ADMIN always has full access
        if "ADMIN" in user_roles:
            return current_user
        
        for role in allowed_roles:
            if role in user_roles:
                return current_user
                
        raise ForbiddenError(
            f"Access denied. User role(s) {user_roles} not authorized. Required: {list(allowed_roles)}"
        )
    return role_checker
