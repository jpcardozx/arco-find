"""
Comprehensive Error Handling Strategy for ARCO.

This module implements a professional error handling system with:
- ProcessingErrorHandler with retry mechanisms
- Exponential backoff for API rate limiting
- Circuit breaker pattern for persistent failures
- Comprehensive logging with structured format
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from dataclasses import dataclass, field
from functools import wraps
import json

T = TypeVar('T')


class ErrorSeverity(Enum):
    """Error severity levels for structured logging."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class ErrorContext:
    """Structured error context for comprehensive logging."""
    operation: str
    service: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    attempt: int = 1
    max_attempts: int = 3
    error_type: str = ""
    error_message: str = ""
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for structured logging."""
        return {
            "operation": self.operation,
            "service": self.service,
            "timestamp": self.timestamp.isoformat(),
            "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "severity": self.severity.value,
            "metadata": self.metadata
        }


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    jitter: bool = True
    retry_on_exceptions: List[Type[Exception]] = field(default_factory=lambda: [
        ConnectionError,
        TimeoutError,
        asyncio.TimeoutError,
        OSError
    ])
    retry_on_status_codes: List[int] = field(default_factory=lambda: [
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504   # Gateway Timeout
    ])


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: Type[Exception] = Exception
    success_threshold: int = 3  # Successes needed to close circuit


class CircuitBreaker:
    """
    Circuit breaker implementation for handling persistent failures.
    
    Prevents cascading failures by temporarily stopping calls to failing services
    and allowing them time to recover.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.logger = logging.getLogger(f"{__name__}.CircuitBreaker")
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to apply circuit breaker to a function."""
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await self.call(func, *args, **kwargs)
        return wrapper
    
    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                self.logger.info("Circuit breaker transitioning to HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Service unavailable until {self._get_reset_time()}"
                )
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return datetime.utcnow() - self.last_failure_time >= timedelta(seconds=self.config.recovery_timeout)
    
    def _get_reset_time(self) -> str:
        """Get the time when circuit breaker will attempt reset."""
        if self.last_failure_time is None:
            return "unknown"
        reset_time = self.last_failure_time + timedelta(seconds=self.config.recovery_timeout)
        return reset_time.isoformat()
    
    def _on_success(self):
        """Handle successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.logger.info("Circuit breaker CLOSED - service recovered")
        elif self.state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
            self.success_count = 0
            self.logger.warning("Circuit breaker OPEN - service still failing")
        elif self.failure_count >= self.config.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.logger.warning(
                f"Circuit breaker OPEN - failure threshold ({self.config.failure_threshold}) exceeded"
            )


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


class APIError(Exception):
    """Base class for API-related errors."""
    pass


class ProcessingErrorHandler:
    """
    Comprehensive error handling with retry mechanisms, exponential backoff,
    and circuit breaker patterns for robust API and service interactions.
    """
    
    def __init__(self, 
                 retry_config: Optional[RetryConfig] = None,
                 circuit_breaker_config: Optional[CircuitBreakerConfig] = None):
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker_config = circuit_breaker_config or CircuitBreakerConfig()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.logger = logging.getLogger(f"{__name__}.ProcessingErrorHandler")
        
        # Configure structured logging
        self._setup_structured_logging()
    
    def _setup_structured_logging(self):
        """Setup structured logging format."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Ensure handler exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(self.circuit_breaker_config)
        return self.circuit_breakers[service_name]
    
    async def process_with_retry(self,
                               operation: Callable[..., T],
                               operation_name: str,
                               service_name: str,
                               *args,
                               **kwargs) -> T:
        """
        Process operation with comprehensive error handling including:
        - Exponential backoff retry
        - Circuit breaker protection
        - Structured error logging
        """
        circuit_breaker = self.get_circuit_breaker(service_name)
        error_context = ErrorContext(
            operation=operation_name,
            service=service_name,
            max_attempts=self.retry_config.max_retries + 1
        )
        
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            error_context.attempt = attempt + 1
            
            try:
                # Apply circuit breaker protection
                result = await circuit_breaker.call(operation, *args, **kwargs)
                
                # Log successful operation if there were previous failures
                if attempt > 0:
                    self._log_success(error_context)
                
                return result
                
            except CircuitBreakerOpenError as e:
                error_context.error_type = "CircuitBreakerOpen"
                error_context.error_message = str(e)
                error_context.severity = ErrorSeverity.HIGH
                self._log_structured_error(error_context)
                raise
                
            except Exception as e:
                last_exception = e
                error_context.error_type = e.__class__.__name__
                error_context.error_message = str(e)
                
                # Determine if we should retry
                should_retry = self._should_retry(e, attempt)
                
                if should_retry and attempt < self.retry_config.max_retries:
                    delay = self._calculate_delay(attempt)
                    error_context.metadata = {
                        "retry_delay": delay,
                        "will_retry": True
                    }
                    error_context.severity = ErrorSeverity.MEDIUM
                    self._log_structured_error(error_context)
                    
                    await asyncio.sleep(delay)
                else:
                    error_context.metadata = {"will_retry": False}
                    error_context.severity = ErrorSeverity.HIGH if attempt == 0 else ErrorSeverity.CRITICAL
                    self._log_structured_error(error_context)
                    break
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        
        raise RuntimeError("Unexpected error in retry logic")
    
    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if an exception should trigger a retry."""
        # Check if exception type is retryable
        for exc_type in self.retry_config.retry_on_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Check for rate limiting
        if isinstance(exception, RateLimitError):
            return True
        
        # Check for API errors with retryable status codes
        if hasattr(exception, 'status_code'):
            return exception.status_code in self.retry_config.retry_on_status_codes
        
        return False
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""
        delay = self.retry_config.initial_delay * (self.retry_config.backoff_factor ** attempt)
        delay = min(delay, self.retry_config.max_delay)
        
        if self.retry_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay
    
    def _log_structured_error(self, error_context: ErrorContext):
        """Log error with structured format."""
        log_data = error_context.to_dict()
        log_message = f"Operation failed: {error_context.operation} (attempt {error_context.attempt}/{error_context.max_attempts})"
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            self.logger.error(f"{log_message} - {json.dumps(log_data)}")
        elif error_context.severity == ErrorSeverity.HIGH:
            self.logger.error(f"{log_message} - {json.dumps(log_data)}")
        elif error_context.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"{log_message} - {json.dumps(log_data)}")
        else:
            self.logger.info(f"{log_message} - {json.dumps(log_data)}")
    
    def _log_success(self, error_context: ErrorContext):
        """Log successful operation after retries."""
        log_data = {
            "operation": error_context.operation,
            "service": error_context.service,
            "timestamp": datetime.utcnow().isoformat(),
            "final_attempt": error_context.attempt,
            "total_attempts": error_context.attempt,
            "status": "success_after_retry"
        }
        self.logger.info(f"Operation succeeded after retries: {error_context.operation} - {json.dumps(log_data)}")


# Decorator for easy application of error handling
def with_error_handling(operation_name: str, 
                       service_name: str,
                       retry_config: Optional[RetryConfig] = None,
                       circuit_breaker_config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator to apply comprehensive error handling to async functions.
    
    Args:
        operation_name: Name of the operation for logging
        service_name: Name of the service for circuit breaker grouping
        retry_config: Custom retry configuration
        circuit_breaker_config: Custom circuit breaker configuration
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        error_handler = ProcessingErrorHandler(retry_config, circuit_breaker_config)
        
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await error_handler.process_with_retry(
                func, operation_name, service_name, *args, **kwargs
            )
        
        return wrapper
    
    return decorator


# Global error handler instance
_global_error_handler: Optional[ProcessingErrorHandler] = None


def get_error_handler() -> ProcessingErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ProcessingErrorHandler()
    return _global_error_handler


def configure_error_handler(retry_config: Optional[RetryConfig] = None,
                          circuit_breaker_config: Optional[CircuitBreakerConfig] = None) -> ProcessingErrorHandler:
    """Configure and return the global error handler."""
    global _global_error_handler
    _global_error_handler = ProcessingErrorHandler(retry_config, circuit_breaker_config)
    return _global_error_handler