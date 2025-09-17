"""
Comprehensive tests for the error handling system.

Tests cover:
- ProcessingErrorHandler functionality
- Retry mechanisms with exponential backoff
- Circuit breaker pattern
- Structured logging
"""

import asyncio
import pytest
import logging
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from arco.core.error_handler import (
    ProcessingErrorHandler,
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerOpenError,
    ErrorContext,
    ErrorSeverity,
    RetryConfig,
    CircuitBreakerConfig,
    RateLimitError,
    APIError,
    with_error_handling,
    get_error_handler,
    configure_error_handler
)


class TestErrorContext:
    """Test ErrorContext functionality."""
    
    def test_error_context_creation(self):
        """Test ErrorContext creation with defaults."""
        context = ErrorContext(operation="test_op", service="test_service")
        
        assert context.operation == "test_op"
        assert context.service == "test_service"
        assert context.attempt == 1
        assert context.max_attempts == 3
        assert context.severity == ErrorSeverity.MEDIUM
        assert isinstance(context.timestamp, datetime)
    
    def test_error_context_to_dict(self):
        """Test ErrorContext serialization to dictionary."""
        context = ErrorContext(
            operation="test_op",
            service="test_service",
            error_type="TestError",
            error_message="Test error message",
            severity=ErrorSeverity.HIGH,
            metadata={"key": "value"}
        )
        
        result = context.to_dict()
        
        assert result["operation"] == "test_op"
        assert result["service"] == "test_service"
        assert result["error_type"] == "TestError"
        assert result["error_message"] == "Test error message"
        assert result["severity"] == "high"
        assert result["metadata"] == {"key": "value"}
        assert "timestamp" in result


class TestCircuitBreaker:
    """Test CircuitBreaker functionality."""
    
    def test_circuit_breaker_initial_state(self):
        """Test circuit breaker starts in CLOSED state."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.success_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_success(self):
        """Test circuit breaker with successful operations."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        async def successful_operation():
            return "success"
        
        result = await breaker.call(successful_operation)
        
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 0
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=2, expected_exception=ValueError)
        breaker = CircuitBreaker(config)
        
        async def failing_operation():
            raise ValueError("Test error")
        
        # First failure
        with pytest.raises(ValueError):
            await breaker.call(failing_operation)
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.failure_count == 1
        
        # Second failure - should open circuit
        with pytest.raises(ValueError):
            await breaker.call(failing_operation)
        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.failure_count == 2
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_rejects_when_open(self):
        """Test circuit breaker rejects calls when open."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=60.0)
        breaker = CircuitBreaker(config)
        
        # Force circuit to open
        breaker.state = CircuitBreakerState.OPEN
        breaker.last_failure_time = datetime.utcnow()
        
        async def any_operation():
            return "should not execute"
        
        with pytest.raises(CircuitBreakerOpenError):
            await breaker.call(any_operation)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through HALF_OPEN state."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=0.1,  # Short timeout for testing
            success_threshold=2
        )
        breaker = CircuitBreaker(config)
        
        # Force circuit to open
        breaker.state = CircuitBreakerState.OPEN
        breaker.last_failure_time = datetime.utcnow() - timedelta(seconds=1)
        
        async def successful_operation():
            return "success"
        
        # First call should transition to HALF_OPEN
        result = await breaker.call(successful_operation)
        assert result == "success"
        assert breaker.state == CircuitBreakerState.HALF_OPEN
        assert breaker.success_count == 1
        
        # Second successful call should close circuit
        result = await breaker.call(successful_operation)
        assert result == "success"
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.success_count == 0
        assert breaker.failure_count == 0


class TestRetryConfig:
    """Test RetryConfig functionality."""
    
    def test_retry_config_defaults(self):
        """Test RetryConfig default values."""
        config = RetryConfig()
        
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_factor == 2.0
        assert config.jitter is True
        assert ConnectionError in config.retry_on_exceptions
        assert 429 in config.retry_on_status_codes
    
    def test_retry_config_custom_values(self):
        """Test RetryConfig with custom values."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            backoff_factor=3.0,
            retry_on_exceptions=[ValueError],
            retry_on_status_codes=[500, 502]
        )
        
        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.backoff_factor == 3.0
        assert config.retry_on_exceptions == [ValueError]
        assert config.retry_on_status_codes == [500, 502]


class TestProcessingErrorHandler:
    """Test ProcessingErrorHandler functionality."""
    
    def test_error_handler_initialization(self):
        """Test ProcessingErrorHandler initialization."""
        handler = ProcessingErrorHandler()
        
        assert handler.retry_config is not None
        assert handler.circuit_breaker_config is not None
        assert isinstance(handler.circuit_breakers, dict)
        assert handler.logger is not None
    
    def test_get_circuit_breaker(self):
        """Test circuit breaker creation and retrieval."""
        handler = ProcessingErrorHandler()
        
        breaker1 = handler.get_circuit_breaker("service1")
        breaker2 = handler.get_circuit_breaker("service1")
        breaker3 = handler.get_circuit_breaker("service2")
        
        assert breaker1 is breaker2  # Same instance for same service
        assert breaker1 is not breaker3  # Different instance for different service
    
    @pytest.mark.asyncio
    async def test_process_with_retry_success(self):
        """Test successful operation without retries."""
        handler = ProcessingErrorHandler()
        
        async def successful_operation():
            return "success"
        
        result = await handler.process_with_retry(
            successful_operation,
            "test_operation",
            "test_service"
        )
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_process_with_retry_with_retries(self):
        """Test operation that succeeds after retries."""
        handler = ProcessingErrorHandler(
            retry_config=RetryConfig(max_retries=2, initial_delay=0.01)
        )
        
        call_count = 0
        
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = await handler.process_with_retry(
            flaky_operation,
            "test_operation",
            "test_service"
        )
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_process_with_retry_exhausted(self):
        """Test operation that fails after all retries."""
        handler = ProcessingErrorHandler(
            retry_config=RetryConfig(max_retries=2, initial_delay=0.01)
        )
        
        async def always_failing_operation():
            raise ConnectionError("Persistent failure")
        
        with pytest.raises(ConnectionError):
            await handler.process_with_retry(
                always_failing_operation,
                "test_operation",
                "test_service"
            )
    
    @pytest.mark.asyncio
    async def test_process_with_circuit_breaker_open(self):
        """Test operation with open circuit breaker."""
        handler = ProcessingErrorHandler(
            circuit_breaker_config=CircuitBreakerConfig(failure_threshold=1)
        )
        
        # Force circuit breaker to open
        breaker = handler.get_circuit_breaker("test_service")
        breaker.state = CircuitBreakerState.OPEN
        breaker.last_failure_time = datetime.utcnow()
        
        async def any_operation():
            return "should not execute"
        
        with pytest.raises(CircuitBreakerOpenError):
            await handler.process_with_retry(
                any_operation,
                "test_operation",
                "test_service"
            )
    
    def test_should_retry_with_retryable_exception(self):
        """Test retry decision for retryable exceptions."""
        handler = ProcessingErrorHandler()
        
        assert handler._should_retry(ConnectionError("test"), 0) is True
        assert handler._should_retry(TimeoutError("test"), 0) is True
        assert handler._should_retry(RateLimitError("test"), 0) is True
        assert handler._should_retry(ValueError("test"), 0) is False
    
    def test_should_retry_with_status_codes(self):
        """Test retry decision for API errors with status codes."""
        handler = ProcessingErrorHandler()
        
        # Mock exception with status code
        api_error = APIError("test")
        api_error.status_code = 429
        
        assert handler._should_retry(api_error, 0) is True
        
        api_error.status_code = 404
        assert handler._should_retry(api_error, 0) is False
    
    def test_calculate_delay(self):
        """Test delay calculation with exponential backoff."""
        config = RetryConfig(
            initial_delay=1.0,
            backoff_factor=2.0,
            max_delay=10.0,
            jitter=False
        )
        handler = ProcessingErrorHandler(retry_config=config)
        
        assert handler._calculate_delay(0) == 1.0
        assert handler._calculate_delay(1) == 2.0
        assert handler._calculate_delay(2) == 4.0
        assert handler._calculate_delay(10) == 10.0  # Capped at max_delay
    
    def test_calculate_delay_with_jitter(self):
        """Test delay calculation with jitter."""
        config = RetryConfig(
            initial_delay=2.0,
            backoff_factor=2.0,
            jitter=True
        )
        handler = ProcessingErrorHandler(retry_config=config)
        
        delay = handler._calculate_delay(1)
        # With jitter, delay should be between 2.0 and 4.0
        assert 2.0 <= delay <= 4.0
    
    @patch('arco.core.error_handler.logging.getLogger')
    def test_structured_logging(self, mock_get_logger):
        """Test structured error logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        handler = ProcessingErrorHandler()
        handler.logger = mock_logger
        
        error_context = ErrorContext(
            operation="test_op",
            service="test_service",
            error_type="TestError",
            error_message="Test message",
            severity=ErrorSeverity.HIGH
        )
        
        handler._log_structured_error(error_context)
        
        # Verify logger was called
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "test_op" in call_args
        assert "TestError" in call_args


class TestDecorator:
    """Test error handling decorator."""
    
    @pytest.mark.asyncio
    async def test_with_error_handling_decorator(self):
        """Test error handling decorator functionality."""
        
        @with_error_handling("test_operation", "test_service")
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_with_error_handling_decorator_with_retry(self):
        """Test error handling decorator with retry."""
        call_count = 0
        
        @with_error_handling(
            "test_operation", 
            "test_service",
            retry_config=RetryConfig(max_retries=2, initial_delay=0.01)
        )
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary failure")
            return "success"
        
        result = await flaky_function()
        assert result == "success"
        assert call_count == 2


class TestGlobalErrorHandler:
    """Test global error handler functions."""
    
    def test_get_error_handler(self):
        """Test global error handler retrieval."""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        
        assert handler1 is handler2  # Should return same instance
        assert isinstance(handler1, ProcessingErrorHandler)
    
    def test_configure_error_handler(self):
        """Test global error handler configuration."""
        custom_config = RetryConfig(max_retries=5)
        handler = configure_error_handler(retry_config=custom_config)
        
        assert isinstance(handler, ProcessingErrorHandler)
        assert handler.retry_config.max_retries == 5
        
        # Should return same instance on subsequent calls
        handler2 = get_error_handler()
        assert handler is handler2


if __name__ == "__main__":
    pytest.main([__file__])