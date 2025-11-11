"""
Push token schemas.

Pydantic models for push token registration and responses.
"""

from pydantic import BaseModel, Field


class PushTokenRegister(BaseModel):
    """Push token registration request schema."""
    
    token: str = Field(..., description="FCM push token")
    platform: str = Field(..., description="Platform: 'ios' or 'android'")
    device_id: str | None = Field(None, description="Device identifier")


class PushTokenResponse(BaseModel):
    """Push token response schema."""
    
    id: str = Field(..., description="Push token ID")
    token: str = Field(..., description="FCM push token")
    platform: str = Field(..., description="Platform")
    is_active: bool = Field(..., description="Is token active")
    
    class Config:
        """Pydantic config."""
        from_attributes = True

