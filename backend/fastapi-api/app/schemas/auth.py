from pydantic import BaseModel, EmailStr
from typing import List, Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: str
    roles: List[str]

class UserProfile(BaseModel):
    user_id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    is_active: bool
    roles: List[str]
    permissions: List[str]
