import logging
import os
import redis
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self):
        logger.info("Initializing MemoryService with Redis")
        # Initialize Redis connection
        redis_host = os.environ.get("REDIS_HOST", "localhost")
        redis_port = int(os.environ.get("REDIS_PORT", 6379))
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            # Fallback to in-memory storage
            self.redis = None
            logger.warning("Using in-memory storage as fallback")
        
        # Local cache for active threads
        self.active_threads: Dict[str, str] = {}
    
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
        
        # Try to get from Redis first
        if self.redis:
            redis_key = f"thread:{identifier}"
            stored_thread = self.redis.get(redis_key)
            if stored_thread:
                self.active_threads[identifier] = stored_thread
                logger.info(f"Retrieved thread ID from Redis for {identifier}: {stored_thread}")
                return stored_thread
        
        # If not found in Redis or Redis is not available, use local cache
        if identifier not in self.active_threads:
            logger.info(f"Creating new thread ID for {identifier}")
            self.active_threads[identifier] = thread_key
            
            # Store in Redis if available
            if self.redis:
                redis_key = f"thread:{identifier}"
                self.redis.set(redis_key, thread_key)
                logger.info(f"Stored thread ID in Redis for {identifier}")
        
        logger.info(f"Thread ID for {identifier}: {self.active_threads[identifier]}")
        return self.active_threads[identifier]
