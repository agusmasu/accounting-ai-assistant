import logging
import os
from typing import Dict, Optional
from langgraph.checkpoint.postgres import PostgresSaver

import psycopg
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self):
        logger.info("Initializing MemoryService with in-memory storage")
        # Local cache for active threads
        self.active_threads: Dict[str, str] = {}
        self.db_host = os.environ.get("POSTGRES_HOST", "localhost")
        self.db_port = os.environ.get("POSTGRES_PORT", 5432)
        self.db_name = os.environ.get("POSTGRES_DB", "appdb")
        self.db_user = os.environ.get("POSTGRES_USER", "postgres")
        self.db_password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        self.db_connect_options = os.environ.get("POSTGRES_CONNECT_OPTIONS", "")
        self.db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require&options={self.db_connect_options}"
        
        # Initialize connection pool and checkpointer
        self.connection_pool = ConnectionPool(
            conninfo=self.db_url,
            max_size=20,
            kwargs={"autocommit": True, "prepare_threshold": 0}
        )
        self.checkpointer = None

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

    def get_thread_id(self, identifier: str, prefix: str = "") -> str:
        """
        Get or create a thread ID for a given identifier (like phone number)
        
        Args:
            identifier: The unique identifier to create a thread for (e.g. phone number)
            prefix: Optional prefix to add to the thread ID
            
        Returns:
            The thread ID
        """
        thread_key = f"{prefix}_{identifier}" if prefix else identifier
        
        # Use local cache
        if identifier not in self.active_threads:
            logger.info(f"Creating new thread ID for {identifier}")
            self.active_threads[identifier] = thread_key
        
        logger.info(f"Thread ID for {identifier}: {self.active_threads[identifier]}")
        return self.active_threads[identifier]
