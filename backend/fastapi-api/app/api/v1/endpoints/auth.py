from fastapi import APIRouter, Depends
from app.schemas.auth import LoginRequest, TokenResponse, UserProfile
from app.services.auth_service import AuthService
from app.core.rbac import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    return AuthService.authenticate_user(credentials.email, credentials.password)

@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict = Depends(get_current_user)):
    return AuthService.get_user_profile(current_user["user_id"])
