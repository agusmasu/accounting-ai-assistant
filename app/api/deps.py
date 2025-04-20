"""Dependency injection for the API endpoints."""
from app.services.ai_service import AIService
from app.services.tusfacturas_service import TusFacturasService
from app.services.whatsapp_service import WhatsAppService
from app.services.memory_service import MemoryService


def get_memory_service():
    """Return a singleton instance of MemoryService."""
    return MemoryService()


def get_ai_service():
    """Return a singleton instance of AIService with MemoryService injected."""
    memory_service = get_memory_service()
    return AIService(memory_service=memory_service)


def get_tusfacturas_service():
    """Return a singleton instance of TusFacturasService."""
    return TusFacturasService()


def get_whatsapp_service():
    """Return a singleton instance of WhatsAppService."""
    return WhatsAppService() 