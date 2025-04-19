import logging
import sys
import json
from pythonjsonlogger import jsonlogger
import os
import re

# Pattern to parse Google Cloud trace context
TRACE_ID_PATTERN = re.compile(r'^([0-9a-f]{32})/(\d+);o=(\d+)$')

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for Google Cloud Logging
    """
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add standard GCP log metadata fields
        log_record["severity"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno
        
        # Add request_id if available
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
            
        # Add custom fields from extra
        for key, value in record.__dict__.items():
            if key not in ['args', 'asctime', 'created', 'exc_info', 'exc_text', 
                           'filename', 'funcName', 'id', 'levelname', 'levelno', 
                           'lineno', 'module', 'msecs', 'message', 'msg', 'name', 
                           'pathname', 'process', 'processName', 'relativeCreated', 
                           'stack_info', 'thread', 'threadName']:
                log_record[key] = value
        
        # Add trace information if available
        trace_context = os.getenv("X_CLOUD_TRACE_CONTEXT")
        if trace_context:
            match = TRACE_ID_PATTERN.match(trace_context)
            if match:
                trace_id = match.group(1)
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
                if project_id:
                    log_record["logging.googleapis.com/trace"] = f"projects/{project_id}/traces/{trace_id}"
                else:
                    log_record["trace_id"] = trace_id

def setup_logging(level=logging.INFO):
    """
    Setup structured JSON logging for Google Cloud
    
    Args:
        level: Logging level to use
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Determine if we're running in Cloud Run
    is_cloud_run = os.getenv("K_SERVICE") is not None
    
    if is_cloud_run:
        # Create JSON formatter for Cloud Logging
        formatter = CustomJsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
        
        # Stream logs to stdout for Cloud Logging to pick up
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    else:
        # If running locally, use a more readable format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger.addHandler(handler)
    
    # Return configured logger
    return root_logger 