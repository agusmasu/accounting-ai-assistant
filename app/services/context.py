import contextvars
from typing import Optional
from app.models.user import User

# Context variable to store the current user
current_user_var = contextvars.ContextVar('current_user', default=None)

class ContextService:
    """Service to manage context variables across the application."""
    
    @staticmethod
    def set_current_user(user: User) -> None:
        """Set the current user in the context.
        
        Args:
            user: The user to set in the context
        """
        current_user_var.set(user)
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """Get the current user from the context.
        
        Returns:
            The current user, or None if not set
        """
        return current_user_var.get() 