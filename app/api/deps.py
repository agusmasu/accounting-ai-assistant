"""Dependency injection for the API endpoints."""
from app.services.ai_service import AIService
from app.services.tusfacturas_service import TusFacturasService
from app.services.whatsapp_service import WhatsAppService


def get_ai_service():
    """Return a singleton instance of AIService."""
    return AIService()


def get_tusfacturas_service():
    """Return a singleton instance of TusFacturasService."""
    return TusFacturasService()


def get_whatsapp_service():
    """Return a singleton instance of WhatsAppService."""
    return WhatsAppService() 