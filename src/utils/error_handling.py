#!/usr/bin/env python3
"""
🛡️ ARCO Error Handling Framework
Centralized error handling and logging for robust operation
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/arco_errors.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ARCOError(Exception):
    """Base exception for ARCO system"""
    def __init__(self, message: str, error_code: str = None, context: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or "GENERIC_ERROR"
        self.context = context or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

class APIError(ARCOError):
    """API-related errors"""
    def __init__(self, message: str, api_name: str, status_code: int = None, **kwargs):
        super().__init__(message, f"API_ERROR_{api_name.upper()}", 
                         {"api": api_name, "status_code": status_code, **kwargs})

class DataValidationError(ARCOError):
    """Data validation errors"""
    def __init__(self, message: str, field: str, value: Any = None, **kwargs):
        super().__init__(message, "DATA_VALIDATION_ERROR", 
                         {"field": field, "value": value, **kwargs})

class ProcessingError(ARCOError):
    """Processing pipeline errors"""
    def __init__(self, message: str, stage: str, prospect_id: str = None, **kwargs):
        super().__init__(message, f"PROCESSING_ERROR_{stage.upper()}", 
                         {"stage": stage, "prospect_id": prospect_id, **kwargs})

def handle_errors(error_types: tuple = (Exception,), default_return=None, log_level="ERROR"):
    """Decorator for handling errors gracefully"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except error_types as e:
                error_msg = f"Error in {func.__name__}: {str(e)}"
                getattr(logger, log_level.lower())(error_msg)
                
                if isinstance(e, ARCOError):
                    logger.error(f"ARCO Error Context: {e.context}")
                
                if log_level == "ERROR":
                    logger.error(f"Traceback: {traceback.format_exc()}")
                
                return default_return
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                error_msg = f"Error in {func.__name__}: {str(e)}"
                getattr(logger, log_level.lower())(error_msg)
                
                if isinstance(e, ARCOError):
                    logger.error(f"ARCO Error Context: {e.context}")
                
                if log_level == "ERROR":
                    logger.error(f"Traceback: {traceback.format_exc()}")
                
                return default_return
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def validate_required_fields(data: dict, required_fields: list, context: str = ""):
    """Validate that required fields are present and non-empty"""
    missing_fields = []
    invalid_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            invalid_fields.append(field)
    
    if missing_fields:
        raise DataValidationError(
            f"Missing required fields in {context}: {', '.join(missing_fields)}",
            field="multiple",
            missing_fields=missing_fields
        )
    
    if invalid_fields:
        raise DataValidationError(
            f"Invalid (empty) fields in {context}: {', '.join(invalid_fields)}",
            field="multiple", 
            invalid_fields=invalid_fields
        )

def log_operation_start(operation: str, context: Dict[str, Any] = None):
    """Log the start of an operation"""
    context_str = f" | Context: {context}" if context else ""
    logger.info(f"🚀 Starting {operation}{context_str}")

def log_operation_success(operation: str, result: Any = None, duration: float = None):
    """Log successful completion of an operation"""
    duration_str = f" | Duration: {duration:.2f}s" if duration else ""
    result_str = f" | Result: {type(result).__name__}" if result else ""
    logger.info(f"✅ Completed {operation}{duration_str}{result_str}")

def log_operation_warning(operation: str, warning: str, context: Dict[str, Any] = None):
    """Log a warning during operation"""
    context_str = f" | Context: {context}" if context else ""
    logger.warning(f"⚠️  Warning in {operation}: {warning}{context_str}")

def log_operation_error(operation: str, error: Exception, context: Dict[str, Any] = None):
    """Log an error during operation"""
    context_str = f" | Context: {context}" if context else ""
    logger.error(f"❌ Error in {operation}: {str(error)}{context_str}")
    
    if isinstance(error, ARCOError):
        logger.error(f"Error Details: {error.context}")

class ErrorTracker:
    """Track and analyze errors for system health monitoring"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
    
    def record_error(self, error: ARCOError):
        """Record an error for tracking"""
        error_type = error.error_code
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        self.error_history.append({
            'timestamp': error.timestamp,
            'type': error_type,
            'message': error.message,
            'context': error.context
        })
        
        # Keep only last 1000 errors to prevent memory issues
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        return {
            'total_errors': len(self.error_history),
            'error_counts': self.error_counts,
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }

# Global error tracker instance
error_tracker = ErrorTracker()

def create_safe_operation(operation_name: str, required_fields: list = None):
    """Create a safe operation context with consistent error handling"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            log_operation_start(operation_name, {"args": len(args), "kwargs": list(kwargs.keys())})
            
            try:
                # Validate required fields if specified
                if required_fields and args:
                    data = args[0] if isinstance(args[0], dict) else kwargs
                    validate_required_fields(data, required_fields, operation_name)
                
                result = await func(*args, **kwargs)
                
                duration = (datetime.now() - start_time).total_seconds()
                log_operation_success(operation_name, result, duration)
                
                return result
                
            except ARCOError as e:
                error_tracker.record_error(e)
                log_operation_error(operation_name, e)
                raise
                
            except Exception as e:
                # Convert generic exceptions to ARCO errors
                arco_error = ProcessingError(
                    f"Unexpected error in {operation_name}: {str(e)}",
                    stage=operation_name
                )
                error_tracker.record_error(arco_error)
                log_operation_error(operation_name, arco_error)
                raise arco_error
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            log_operation_start(operation_name, {"args": len(args), "kwargs": list(kwargs.keys())})
            
            try:
                # Validate required fields if specified
                if required_fields and args:
                    data = args[0] if isinstance(args[0], dict) else kwargs
                    validate_required_fields(data, required_fields, operation_name)
                
                result = func(*args, **kwargs)
                
                duration = (datetime.now() - start_time).total_seconds()
                log_operation_success(operation_name, result, duration)
                
                return result
                
            except ARCOError as e:
                error_tracker.record_error(e)
                log_operation_error(operation_name, e)
                raise
                
            except Exception as e:
                # Convert generic exceptions to ARCO errors
                arco_error = ProcessingError(
                    f"Unexpected error in {operation_name}: {str(e)}",
                    stage=operation_name
                )
                error_tracker.record_error(arco_error)
                log_operation_error(operation_name, arco_error)
                raise arco_error
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Ensure logs directory exists
import os
os.makedirs('logs', exist_ok=True)

if __name__ == "__main__":
    # Test the error handling system
    @create_safe_operation("test_operation", required_fields=["name", "email"])
    def test_function(data):
        if data["name"] == "error":
            raise ValueError("Test error")
        return f"Hello {data['name']}"
    
    # Test successful operation
    print(test_function({"name": "John", "email": "john@example.com"}))
    
    # Test validation error
    try:
        test_function({"name": ""})
    except DataValidationError as e:
        print(f"Validation error: {e}")
    
    # Test processing error
    try:
        test_function({"name": "error", "email": "test@example.com"})
    except ProcessingError as e:
        print(f"Processing error: {e}")
    
    # Show error summary
    print("\nError Summary:", error_tracker.get_error_summary())