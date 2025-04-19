# FacturAI Logging System

This document describes the logging system for the FacturAI application, which is designed to work optimally with Google Cloud Logging when deployed to Cloud Run.

## Overview

The logging system is built on Python's standard `logging` module, enhanced with the following features:

1. **Structured JSON Logs**: All logs in Cloud Run are formatted as JSON for better integration with Google Cloud Logging
2. **Request Tracing**: Each request gets a unique ID that's included in all related log entries
3. **Cloud Trace Integration**: Automatic integration with Google Cloud Trace for distributed tracing
4. **Middleware**: Automatic logging of request/response information via FastAPI middleware
5. **Local Development**: Human-readable logs in local development for easier debugging

## Usage

### Basic Logging

```python
import logging

# Get a logger for your module
logger = logging.getLogger(__name__)

# Log at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message", exc_info=True)  # Include exception info
```

### Request-Aware Logging

For logging in request handlers, use the `get_request_logger` utility:

```python
from app.utils.logger import get_request_logger

@app.get("/some-endpoint")
async def some_endpoint(request: Request):
    # Get a logger with request context
    logger = get_request_logger(request, __name__)
    
    # All logs will include the request_id
    logger.info("Processing request")
    
    # You can add extra fields
    logger.info(
        "User action performed", 
        extra={
            "user_id": "123",
            "action": "login"
        }
    )
```

### Structured Logging

You can include additional structured data with any log message:

```python
logger.info(
    "Processing payment", 
    extra={
        "payment_id": "pmt_123456",
        "amount": 100.50,
        "currency": "USD"
    }
)
```

## Configuration

The logging system is configured in `app/logging_config.py`. The main configuration function is `setup_logging()`, which is called from `main.py`.

It automatically detects if the application is running in Cloud Run by checking for the `K_SERVICE` environment variable.

## Viewing Logs

### In Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Logging** > **Logs Explorer**
3. Select your Cloud Run service from the resource dropdown
4. Filter logs with queries like:
   - `severity>=WARNING` - Show warnings and errors
   - `jsonPayload.request_id="abc123"` - Find all logs for a specific request
   - `jsonPayload.user_id="123"` - Find all logs for a specific user

### Local Development

In local development, logs are printed to the console in a human-readable format.

## Middleware

The `RequestLoggingMiddleware` automatically logs information about each request:
- Request method and path
- Query parameters
- Client IP
- Response status code
- Processing time

## Best Practices

1. **Use the right log level**:
   - `DEBUG`: Detailed debug information
   - `INFO`: Confirmation that things are working as expected
   - `WARNING`: Something unexpected happened, but the application can continue
   - `ERROR`: A serious problem occurred that needs attention

2. **Include context**: Add relevant IDs and data to help troubleshoot issues

3. **Log exceptions properly**: Use `exc_info=True` when logging exceptions

4. **Add structured data**: Use the `extra` parameter to add structured data to logs 