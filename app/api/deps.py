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
from sqlmodel import Session
import os

# API Key header for admin authentication
api_key_header = APIKeyHeader(name="X-Admin-API-Key")

def get_db_session():
    """Get database session."""
    db = Db()
    try:
        yield db.session
    finally:
        db.session.close()

def get_user_service(db_session: Session = Depends(get_db_session)):
    """Get user service instance."""
    return UserService(db_session=db_session)

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

def get_conversation_service(db_session: Session = Depends(get_db_session)):
    """Return a singleton instance of ConversationService."""
    return ConversationService(db_session=db_session)

def get_memory_service(
    user_service: UserService = Depends(get_user_service),
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Return a singleton instance of MemoryService."""
    return MemoryService(conversation_service=conversation_service, user_service=user_service)


def get_ai_service(memory_service: MemoryService = Depends(get_memory_service), conversation_service: ConversationService = Depends(get_conversation_service), user_service: UserService = Depends(get_user_service)):
    """Return a singleton instance of AIService with MemoryService injected."""
    return AIService(memory_service=memory_service, conversation_service=conversation_service, user_service=user_service)


def get_tusfacturas_service(user_service: UserService = Depends(get_user_service)):
    """Return a singleton instance of TusFacturasService."""
    return TusFacturasService(user_service=user_service)


def get_whatsapp_service(memory_service: MemoryService = Depends(get_memory_service)):
    """Return a singleton instance of WhatsAppService."""
    return WhatsAppService(memory_service=memory_service)