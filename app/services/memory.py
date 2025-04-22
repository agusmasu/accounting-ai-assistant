import logging
import os
from typing import Dict, Optional
from fastapi import Depends, HTTPException
from langgraph.checkpoint.postgres import PostgresSaver
from sqlmodel import Session

import psycopg
from psycopg_pool import ConnectionPool
from app.models.conversation import Conversation
from app.models.user import User
from app.services.conversation import ConversationService
from app.services.user import UserService

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, conversation_service: ConversationService, user_service: UserService):
        logger.info("Initializing MemoryService with in-memory storage")
        # Local cache for active threads
        self.active_threads: Dict[str, str] = {}
        self.db_host = os.environ.get("POSTGRES_HOST", "localhost")
        self.db_port = os.environ.get("POSTGRES_PORT", 5432)
        self.db_name = os.environ.get("POSTGRES_DB", "appdb")
        self.db_user = os.environ.get("POSTGRES_USER", "postgres")
        self.db_password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        self.db_connect_options = os.environ.get("POSTGRES_CONNECT_OPTIONS", "")
        # Use percent encoding for the options parameter
        if self.db_connect_options:
            self.db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require&options={self.db_connect_options.replace('=', '%3D')}"
        else:
            self.db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require"
        
        # Initialize connection pool and checkpointer
        self.connection_pool = ConnectionPool(
            conninfo=self.db_url,
            max_size=20,
            kwargs={"autocommit": True, "prepare_threshold": 0}
        )
        self.checkpointer = None
        self.conversation_service = conversation_service
        self.user_service = user_service
    @classmethod
    def get_service(cls, conversation_service: ConversationService = Depends(ConversationService.get_service)):
        return cls(conversation_service)

    def get_checkpointer(self):
        """
        Get or create a checkpoint for a given identifier (like phone number)
        
        Returns:
            The PostgresSaver checkpointer
        """        
        if self.checkpointer is None:
            self.checkpointer = PostgresSaver(self.connection_pool)
            # NOTE: you need to call .setup() the first time you're using your checkpointer
            self.checkpointer.setup()
        
        return self.checkpointer

    def get_thread_id(self, phone_number: str) -> str:
        """
        Get or create a thread ID for a given identifier (like phone number)
        
        Args:
            identifier: The unique identifier to create a thread for (e.g. phone number)
            prefix: Optional prefix to add to the thread ID
            
        Returns:
            The thread ID
        """
        logger.info(f"Getting thread ID for {phone_number}")
        user: User = self.user_service.get_user_by_phone_number(phone_number)
        if user is None:
            logger.error(f"User not found for phone number {phone_number}")
            raise HTTPException(status_code=404, detail="User not found")
        else:
            logger.info(f"User found for phone number {phone_number}")
            current_conversation: Conversation = self.conversation_service.get_current_conversation(user.id)
            return current_conversation.thread_id