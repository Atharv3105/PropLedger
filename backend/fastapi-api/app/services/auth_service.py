from app.core.database import get_db_cursor
from app.core.security import verify_password, create_access_token
from app.core.exceptions import UnauthorizedError, NotFoundError

class AuthService:
    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT u.user_id, u.email, u.password_hash, u.full_name, u.is_active
                FROM users u
                WHERE LOWER(u.email) = LOWER(%s);
            """, (email,))
            user = cur.fetchone()
            
            if not user or not verify_password(password, user["password_hash"]):
                raise UnauthorizedError("Invalid email or password")
            
            if not user["is_active"]:
                raise UnauthorizedError("User account is inactive")
            
            # Fetch roles
            cur.execute("""
                SELECT r.role_name
                FROM roles r
                JOIN user_roles ur ON r.role_id = ur.role_id
                WHERE ur.user_id = %s;
            """, (user["user_id"],))
            roles = [r["role_name"] for r in cur.fetchall()]
            
            token_payload = {
                "sub": str(user["user_id"]),
                "email": user["email"],
                "roles": roles
            }
            token = create_access_token(token_payload)
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 7200,
                "user_id": user["user_id"],
                "email": user["email"],
                "roles": roles
            }

    @staticmethod
    def get_user_profile(user_id: int) -> dict:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT user_id, email, full_name, phone, is_active
                FROM users
                WHERE user_id = %s;
            """, (user_id,))
            user = cur.fetchone()
            if not user:
                raise NotFoundError("User not found")
            
            cur.execute("""
                SELECT r.role_name
                FROM roles r
                JOIN user_roles ur ON r.role_id = ur.role_id
                WHERE ur.user_id = %s;
            """, (user_id,))
            user["roles"] = [r["role_name"] for r in cur.fetchall()]
            
            cur.execute("""
                SELECT DISTINCT p.permission_code
                FROM permissions p
                JOIN role_permissions rp ON p.permission_id = rp.permission_id
                JOIN user_roles ur ON rp.role_id = ur.role_id
                WHERE ur.user_id = %s;
            """, (user_id,))
            user["permissions"] = [p["permission_code"] for p in cur.fetchall()]
            
            return user
