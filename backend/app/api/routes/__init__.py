from fastapi import APIRouter

from . import rooms, users, cards

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(rooms.router)
api_router.include_router(cards.router)
