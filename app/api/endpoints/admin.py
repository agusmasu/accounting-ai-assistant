"""Admin API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.user import UserService
from app.models.user import User
from app.api.deps import get_user_service, verify_admin_api_key
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])

class CreateUserRequest(BaseModel):
    """Request model for user creation."""
    name: str
    email: str
    phone_number: str
    user_token: Optional[str] = None

@router.post("/users", response_model=User)
async def create_user(
    user_data: CreateUserRequest,
    user_service: UserService = Depends(get_user_service),
    _: str = Depends(verify_admin_api_key)  # Verify admin API key
):
    """
    Create a new user (Admin only).
    """
    # Check if user with same email or phone number exists
    existing_user = user_service.get_user_by_phone_number(user_data.phone_number)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this phone number already exists"
        )
    
    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        user_token=user_data.user_token
    )
    
    try:
        created_user = user_service.create_user(new_user)
        return created_user
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create user: {str(e)}"
        ) 