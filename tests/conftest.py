import pytest
import os
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure pytest
def pytest_configure(config):
    # Add custom markers
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as async"
    ) 