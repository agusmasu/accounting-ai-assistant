import pytest
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure pytest
def pytest_configure(config):
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    ) 