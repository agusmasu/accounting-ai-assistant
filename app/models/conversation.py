import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime

class Conversation(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime | None = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=datetime.now())
    user_id: str | None = Field(default=None)
    thread_id: str | None = Field(default=None)
    last_message_at: datetime | None = Field(default=datetime.now())