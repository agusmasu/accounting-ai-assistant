from typing import Optional
from sqlmodel import Session, select
from app.models.user import User
from app.db import Db
from fastapi import Depends
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        statement = select(User).where(User.id == user_id)
        result = self.db_session.exec(statement).first()
        return result

    def create_user(self, user: User) -> User:
        try:
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            return user
        except Exception as e:
            self.db_session.rollback()
            raise e

    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Update the user fields
        for key, value in user_data.items():
            setattr(user, key, value)
        
        # Always update the updated_at timestamp
        user.updated_at = datetime.now()
        
        try:
            self.db_session.commit()
            # Refresh the user object to get the latest data
            self.db_session.refresh(user)
            return user
        except Exception as e:
            self.db_session.rollback()
            raise e

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        try:
            self.db_session.delete(user)
            self.db_session.commit()
            return True
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def get_user_by_phone_number(self, phone_number: str) -> Optional[User]:
        logger.info(f"Getting user by phone number: {phone_number}")
        statement = select(User).where(User.phone_number == phone_number)
        result = self.db_session.exec(statement).first()
        return result
    
    def get_all_users(self) -> list[User]:
        statement = select(User)
        result = self.db_session.exec(statement).all()
        return result