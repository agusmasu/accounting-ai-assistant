from datetime import datetime, timedelta

from fastapi import Depends
from sqlmodel import Session, select, update, insert
from app.db import Db
from app.models.conversation import Conversation
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_conversation(self, user_id: str) -> Conversation:
        # Create a thread id , with the user id and the current datetime:
        thread_id = f"{user_id}-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
        conversation = Conversation(user_id=user_id, thread_id=thread_id)
        self.db_session.add(conversation)
        self.db_session.commit()
        return conversation
    
    def _should_create_new_conversation(self, user_id: str, last_conversation: Conversation) -> bool:
        """
        If there is no last conversation, or the last conversation is older than 30 minutes, create a new conversation.
        """
        if not last_conversation:
            return True
        if last_conversation.last_message_at < datetime.now() - timedelta(minutes=30):
            return True
        return False

    def get_current_conversation(self, user_id: str) -> Conversation:
        # Get the most recent conversation for the user
        statement = select(Conversation).where(Conversation.user_id == user_id).order_by(Conversation.last_message_at.desc())
        conversation = self.db_session.exec(statement).first()
        if conversation is None:
            logger.info(f"No conversation found for user {user_id}, creating new conversation")
            return self.create_conversation(user_id)
        if self._should_create_new_conversation(user_id, conversation):
            logger.info(f"Creating new conversation for user {user_id}")
            return self.create_conversation(user_id)
        logger.info(f"Returning conversation {conversation.id} for user {user_id}")
        return conversation
    
    def update_last_message_at(self, conversation_id: str):
        statement = update(Conversation).where(Conversation.id == conversation_id).values(last_message_at=datetime.now())
        self.db_session.exec(statement)
        self.db_session.commit()
    
    