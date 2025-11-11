"""
Logout endpoint.

Handles user logout and token blacklisting.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.database.database import get_db
from src.database.models import TokenBlacklist
from src.core.security import decode_token, get_jti_from_token
from src.schemas.auth import LogoutRequest

router = APIRouter()


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db),
):
    """
    Logout user and blacklist tokens.
    
    Args:
        logout_data: Access and refresh tokens to blacklist
        db: Database session
        
    Returns:
        Success message
    """
    # Decode tokens to get expiration and user info
    access_payload = decode_token(logout_data.access_token)
    refresh_payload = decode_token(logout_data.refresh_token)
    
    if not access_payload or not refresh_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tokens",
        )
    
    user_id = access_payload.get("sub") or refresh_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload",
        )
    
    # Blacklist access token
    access_jti = get_jti_from_token(logout_data.access_token) or access_payload.get("jti")
    if access_jti:
        blacklist_entry = TokenBlacklist(
            jti=access_jti,
            user_id=user_id,
            token_type="access",
            expires_at=datetime.fromtimestamp(access_payload.get("exp", 0)),
            reason="logout",
        )
        db.add(blacklist_entry)
    
    # Blacklist refresh token
    refresh_jti = get_jti_from_token(logout_data.refresh_token) or refresh_payload.get("jti")
    if refresh_jti:
        blacklist_entry = TokenBlacklist(
            jti=refresh_jti,
            user_id=user_id,
            token_type="refresh",
            expires_at=datetime.fromtimestamp(refresh_payload.get("exp", 0)),
            reason="logout",
        )
        db.add(blacklist_entry)
    
    db.commit()
    
    return {"message": "Successfully logged out"}

