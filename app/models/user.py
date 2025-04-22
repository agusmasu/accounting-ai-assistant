from datetime import datetime
from sqlmodel import Field, SQLModel
import uuid

class User(SQLModel, table=True):
    id: str | None = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(default=None)
    email: str = Field(default=None)
    user_token: str | None = Field(default=None)
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)
    phone_number: str = Field(default=None, unique=True, index=True)