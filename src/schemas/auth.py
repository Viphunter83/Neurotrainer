"""
Authentication schemas.

Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class RegisterRequest(BaseModel):
    """Registration request schema."""
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: str | None = Field(None, max_length=255, description="Full name")


class TokenResponse(BaseModel):
    """Token response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    
    refresh_token: str = Field(..., description="Refresh token")


class LogoutRequest(BaseModel):
    """Logout request schema."""
    
    access_token: str = Field(..., description="Access token to blacklist")
    refresh_token: str = Field(..., description="Refresh token to blacklist")


class UserResponse(BaseModel):
    """User response schema."""
    
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address")
    username: str = Field(..., description="Username")
    full_name: str | None = Field(None, description="Full name")
    is_active: bool = Field(..., description="Is user active")
    created_at: str | None = Field(None, description="Account creation date")
    
    class Config:
        """Pydantic config."""
        from_attributes = True

