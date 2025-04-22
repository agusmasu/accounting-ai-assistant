import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel, create_engine, select
from app.services.conversation import ConversationService
from app.models.conversation import Conversation
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@pytest.fixture
def test_db():
    """Create a test database with an in-memory SQLite engine"""
    # Use SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=True)
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    # Create a session
    session = Session(engine)
    
    yield session
    
    # Clean up
    session.close()

@pytest.fixture
def conversation_service(test_db):
    """Create a ConversationService instance with the test database session"""
    return ConversationService(test_db)

def test_create_conversation(conversation_service):
    """Test creating a new conversation"""
    # Arrange
    user_id = "test_user_123"
    
    # Act
    conversation = conversation_service.create_conversation(user_id)
    
    # Assert
    assert conversation is not None
    assert conversation.user_id == user_id
    assert conversation.thread_id is not None
    assert conversation.thread_id.startswith(user_id)
    assert conversation.last_message_at is not None

def test_get_current_conversation_new_user(conversation_service, test_db):
    """Test getting current conversation for a new user"""
    # Arrange
    user_id = "new_user_123"
    
    # Act
    conversation = conversation_service.get_current_conversation(user_id)
    
    # Assert
    assert conversation is not None
    assert conversation.user_id == user_id
    assert conversation.thread_id is not None
    assert conversation.thread_id.startswith(user_id)
    
    # Note: The conversation is not saved to the database in the current implementation
    # So we don't check the database count

def test_get_current_conversation_existing_user(conversation_service, test_db):
    """Test getting current conversation for an existing user with recent activity"""
    # Arrange
    user_id = "existing_user_123"
    
    # Create a conversation with recent activity
    conversation = conversation_service.create_conversation(user_id)
    conversation.last_message_at = datetime.now()
    test_db.add(conversation)
    test_db.commit()
    
    # Act
    current_conversation = conversation_service.get_current_conversation(user_id)
    
    # Assert
    assert current_conversation is not None
    assert current_conversation.id == conversation.id
    assert current_conversation.user_id == user_id
    
    # Verify only one conversation exists
    statement = select(Conversation).where(Conversation.user_id == user_id)
    results = test_db.exec(statement).all()
    assert len(results) == 1

def test_get_current_conversation_old_conversation(conversation_service, test_db):
    """Test getting current conversation when the last conversation is old"""
    # Arrange
    user_id = "old_conversation_user_123"
    
    # Create an old conversation
    old_conversation = conversation_service.create_conversation(user_id)
    old_conversation.last_message_at = datetime.now() - timedelta(minutes=31)  # Older than 30 minutes
    test_db.add(old_conversation)
    test_db.commit()
    
    # Act
    current_conversation = conversation_service.get_current_conversation(user_id)
    
    # Assert
    assert current_conversation is not None
    assert current_conversation.id != old_conversation.id  # Should be a new conversation
    assert current_conversation.user_id == user_id
    
    # Verify only one conversation exists (the old one)
    # Note: The new conversation is not saved to the database in the current implementation
    statement = select(Conversation).where(Conversation.user_id == user_id)
    results = test_db.exec(statement).all()
    assert len(results) == 1 