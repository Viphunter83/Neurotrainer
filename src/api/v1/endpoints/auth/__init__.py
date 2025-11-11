"""Authentication endpoints."""

from fastapi import APIRouter

from src.api.v1.endpoints.auth import login, register, refresh, logout

router = APIRouter()

router.include_router(login.router)
router.include_router(register.router)
router.include_router(refresh.router)
router.include_router(logout.router)

