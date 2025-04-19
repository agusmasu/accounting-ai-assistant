import logging
from fastapi import Request

def get_request_logger(request: Request = None, logger_name: str = None):
    """
    Get a logger with request context information
    
    Args:
        request: FastAPI request object, if available
        logger_name: Name for the logger, defaults to the module name
        
    Returns:
        A configured logger with request context
    """
    if logger_name is None:
        # Get the calling module's name
        import inspect
        frame = inspect.currentframe().f_back
        module = inspect.getmodule(frame)
        logger_name = module.__name__
        
    logger = logging.getLogger(logger_name)
    
    # If we have a request, check for request_id to add to logging context
    if request and hasattr(request.state, 'request_id'):
        # Create a filter to add request_id to all log records
        class RequestFilter(logging.Filter):
            def filter(self, record):
                record.request_id = request.state.request_id
                return True
                
        # Add the filter to the logger
        for handler in logging.getLogger().handlers:
            handler.addFilter(RequestFilter())
            
    return logger 