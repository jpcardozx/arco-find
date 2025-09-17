"""
Comprehensive Error Handling Example for ARCO.

This example demonstrates the professional error handling system with:
- ProcessingErrorHandler with retry mechanisms
- Exponential backoff for API rate limiting
- Circuit breaker pattern for persistent failures
- Comprehensive logging with structured format
"""

import asyncio
import logging
from datetime import datetime

from arco.core.error_handler import (
    ProcessingErrorHandler,
    RetryConfig,
    CircuitBreakerConfig,
    with_error_handling,
    RateLimitError,
    APIError,
    get_error_handler
)
from arco.core.container import ServiceContainer
from arco.core.service_configuration import configure_all_services, get_business_intelligence_service


# Configure logging to see the structured error logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MockAPIService:
    """Mock API service to demonstrate error handling patterns."""
    
    def __init__(self):
        self.call_count = 0
        self.failure_count = 0
    
    @with_error_handling(
        "mock_api_call",
        "mock_service",
        retry_config=RetryConfig(
            max_retries=3,
            initial_delay=0.5,
            backoff_factor=2.0,
            max_delay=5.0
        )
    )
    async def flaky_api_call(self, data: str) -> str:
        """Simulate a flaky API that sometimes fails."""
        self.call_count += 1
        
        # Simulate different types of failures
        if self.call_count <= 2:
            if self.call_count == 1:
                raise ConnectionError("Network connection failed")
            elif self.call_count == 2:
                raise RateLimitError("API rate limit exceeded")
        
        # Success on third attempt
        return f"Success: Processed {data} on attempt {self.call_count}"
    
    @with_error_handling(
        "persistent_failure_api",
        "failing_service",
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=2.0
        )
    )
    async def persistent_failure_api(self, data: str) -> str:
        """Simulate an API that persistently fails to trigger circuit breaker."""
        self.failure_count += 1
        raise APIError(f"Persistent API failure #{self.failure_count}")


async def demonstrate_retry_mechanism():
    """Demonstrate retry mechanism with exponential backoff."""
    logger.info("🔄 Demonstrating Retry Mechanism with Exponential Backoff")
    
    service = MockAPIService()
    
    try:
        result = await service.flaky_api_call("test data")
        logger.info(f"✅ API call succeeded: {result}")
    except Exception as e:
        logger.error(f"❌ API call failed after all retries: {e}")
    
    logger.info(f"📊 Total API calls made: {service.call_count}")


async def demonstrate_circuit_breaker():
    """Demonstrate circuit breaker pattern for persistent failures."""
    logger.info("\n⚡ Demonstrating Circuit Breaker Pattern")
    
    service = MockAPIService()
    
    # Make several calls to trigger circuit breaker
    for i in range(6):
        try:
            result = await service.persistent_failure_api(f"data_{i}")
            logger.info(f"✅ Call {i+1} succeeded: {result}")
        except Exception as e:
            logger.warning(f"⚠️ Call {i+1} failed: {e}")
        
        # Small delay between calls
        await asyncio.sleep(0.1)
    
    logger.info(f"📊 Total failure attempts: {service.failure_count}")


async def demonstrate_business_intelligence_error_handling():
    """Demonstrate error handling in actual business intelligence service."""
    logger.info("\n🧠 Demonstrating Business Intelligence Service Error Handling")
    
    # Configure the service container
    container = ServiceContainer()
    configure_all_services(container)
    
    # Get the business intelligence service
    bi_service = get_business_intelligence_service(container)
    
    # Test with a real domain
    try:
        intelligence = await bi_service.collect_intelligence("example.com", "Example Corporation")
        logger.info(f"✅ Intelligence collected successfully")
        logger.info(f"📊 Data Quality Score: {intelligence.data_quality_score:.2f}")
        logger.info(f"📈 Ad Investment Active: {intelligence.ad_investment.facebook_active or intelligence.ad_investment.google_active}")
        logger.info(f"💰 Funding Profile: {intelligence.funding_profile.recent_funding_months is not None}")
    except Exception as e:
        logger.error(f"❌ Intelligence collection failed: {e}")


async def demonstrate_custom_error_handler():
    """Demonstrate creating a custom error handler with specific configuration."""
    logger.info("\n⚙️ Demonstrating Custom Error Handler Configuration")
    
    # Create custom error handler with aggressive retry settings
    custom_error_handler = ProcessingErrorHandler(
        retry_config=RetryConfig(
            max_retries=5,
            initial_delay=0.1,
            backoff_factor=1.5,
            max_delay=2.0,
            jitter=True
        ),
        circuit_breaker_config=CircuitBreakerConfig(
            failure_threshold=2,
            recovery_timeout=1.0,
            success_threshold=1
        )
    )
    
    # Test custom error handler
    call_count = 0
    
    async def custom_operation():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"Temporary failure #{call_count}")
        return f"Success after {call_count} attempts"
    
    try:
        result = await custom_error_handler.process_with_retry(
            custom_operation,
            "custom_operation",
            "custom_service"
        )
        logger.info(f"✅ Custom operation succeeded: {result}")
    except Exception as e:
        logger.error(f"❌ Custom operation failed: {e}")


async def demonstrate_structured_logging():
    """Demonstrate structured error logging capabilities."""
    logger.info("\n📝 Demonstrating Structured Error Logging")
    
    error_handler = get_error_handler()
    
    async def logging_test_operation():
        # Simulate an operation with rich context
        raise APIError("Detailed API error with context")
    
    try:
        await error_handler.process_with_retry(
            logging_test_operation,
            "structured_logging_test",
            "logging_service"
        )
    except Exception as e:
        logger.info("✅ Structured error logging demonstrated (check logs above)")


async def main():
    """Run all error handling demonstrations."""
    logger.info("🚀 Starting ARCO Error Handling Demonstration")
    logger.info("=" * 60)
    
    try:
        await demonstrate_retry_mechanism()
        await demonstrate_circuit_breaker()
        await demonstrate_business_intelligence_error_handling()
        await demonstrate_custom_error_handler()
        await demonstrate_structured_logging()
        
        logger.info("\n" + "=" * 60)
        logger.info("🎉 Error Handling Demonstration Completed Successfully!")
        logger.info("\nKey Features Demonstrated:")
        logger.info("✅ Exponential backoff retry mechanism")
        logger.info("✅ Circuit breaker pattern for persistent failures")
        logger.info("✅ Structured error logging with JSON metadata")
        logger.info("✅ Graceful degradation in business services")
        logger.info("✅ Custom error handler configuration")
        logger.info("✅ Integration with dependency injection container")
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())