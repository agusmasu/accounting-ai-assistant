"""Main API router."""
from fastapi import APIRouter
from app.api.endpoints import whatsapp, chat, admin

# Main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(whatsapp.router)
api_router.include_router(chat.router)
api_router.include_router(admin.router) 