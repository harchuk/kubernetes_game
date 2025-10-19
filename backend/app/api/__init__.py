from fastapi import APIRouter

from .routes import api_router as routes_router

api_router = APIRouter()
api_router.include_router(routes_router)

__all__ = ["api_router"]
