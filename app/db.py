from sqlmodel import create_engine, Session, SQLModel
# Import all models here
from app.models.user import *
from app.models.invoice import *
from app.models.conversation import *
import os

class Db:
    def __init__(self):
        self.db_host = os.environ.get("POSTGRES_HOST", "localhost")
        self.db_port = os.environ.get("POSTGRES_PORT", 5432)
        self.db_name = os.environ.get("POSTGRES_DB", "appdb")
        self.db_user = os.environ.get("POSTGRES_USER", "postgres")
        self.db_password = os.environ.get("POSTGRES_PASSWORD", "postgres")
        self.db_connect_options = os.environ.get("POSTGRES_CONNECT_OPTIONS", "")
        # Use percent encoding for the options parameter
        if self.db_connect_options:
            self.db_url = f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require&options={self.db_connect_options.replace('=', '%3D')}"
        else:
            self.db_url = f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require"
        
        self.engine = create_engine(self.db_url)
        self.session = Session(self.engine)

    def create_all(self):
        SQLModel.metadata.create_all(self.engine)