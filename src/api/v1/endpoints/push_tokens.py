"""
Push token management endpoints.

Handles registration and deactivation of FCM push tokens.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from src.database.database import get_db
from src.database.models import PushToken, User
from src.core.dependencies import get_current_user_id
from src.schemas.push_tokens import PushTokenRegister, PushTokenResponse

router = APIRouter()


@router.post("/push-tokens/register", response_model=PushTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_push_token(
    token_data: PushTokenRegister,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Register a push token for the current user.
    
    Args:
        token_data: Push token information
        db: Database session
        user_id: Current user ID from JWT
        
    Returns:
        Registered push token information
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if token already exists
    existing_token = db.query(PushToken).filter(
        PushToken.token == token_data.token
    ).first()
    
    if existing_token:
        # Update existing token
        existing_token.user_id = user_id
        existing_token.platform = token_data.platform
        existing_token.device_id = token_data.device_id
        existing_token.is_active = True
        from datetime import datetime
        existing_token.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_token)
        
        return PushTokenResponse(
            id=str(existing_token.id),
            token=existing_token.token,
            platform=existing_token.platform,
            is_active=existing_token.is_active,
        )
    
    # Create new token
    new_token = PushToken(
        user_id=user_id,
        token=token_data.token,
        platform=token_data.platform,
        device_id=token_data.device_id,
        is_active=True,
    )
    
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    
    return PushTokenResponse(
        id=str(new_token.id),
        token=new_token.token,
        platform=new_token.platform,
        is_active=new_token.is_active,
    )


@router.post("/push-tokens/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_push_token(
    token_data: dict,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
):
    """
    Deactivate a push token.
    
    Args:
        token_data: Dictionary with 'token' key
        db: Database session
        user_id: Current user ID from JWT
    """
    token = token_data.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required",
        )
    
    push_token = db.query(PushToken).filter(
        PushToken.token == token,
        PushToken.user_id == user_id,
    ).first()
    
    if not push_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Push token not found",
        )
    
    push_token.is_active = False
    db.commit()
    
    return {"message": "Push token deactivated successfully"}

