from datetime import datetime
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    email: str = Field(default=None)
    user_token: str | None = Field(default=None)
    created_at: datetime | None = Field(default=datetime.now())
    updated_at: datetime | None = Field(default=datetime.now())
    phone_number: str = Field(default=None, )