"""Dependency injection for the API endpoints."""
from app.services.ai import AIService
from app.services.conversation import ConversationService
from app.services.tusfacturas import TusFacturasService
from app.services.whatsapp import WhatsAppService
from app.services.memory import MemoryService
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from app.services.user import UserService
from app.db import Db
import os

# API Key header for admin authentication
api_key_header = APIKeyHeader(name="X-Admin-API-Key")

async def get_user_service(db_session=Depends(lambda: Db().session)):
    """Get user service instance."""
    return UserService.get_service(db_session)

async def verify_admin_api_key(api_key: str = Security(api_key_header)):
    """Verify admin API key."""
    admin_api_key = os.getenv("ADMIN_API_KEY")
    if not admin_api_key:
        raise HTTPException(
            status_code=500,
            detail="Admin API key not configured"
        )
    if api_key != admin_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin API key"
        )
    return api_key

def get_conversation_service(db_session=Depends(lambda: Db().session)):
    """Return a singleton instance of ConversationService."""
    return ConversationService(db_session=db_session)

def get_memory_service():
    """Return a singleton instance of MemoryService."""
    user_service = get_user_service()
    conversation_service = get_conversation_service()
    return MemoryService(conversation_service=conversation_service, user_service=user_service)


def get_ai_service():
    """Return a singleton instance of AIService with MemoryService injected."""
    memory_service = get_memory_service()
    return AIService(memory_service=memory_service)


def get_tusfacturas_service():
    """Return a singleton instance of TusFacturasService."""
    return TusFacturasService()


def get_whatsapp_service():
    """Return a singleton instance of WhatsAppService."""
    memory_service = get_memory_service()
    return WhatsAppService(memory_service=memory_service)