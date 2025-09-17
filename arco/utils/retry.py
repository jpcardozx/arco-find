"""
Retry and Fallback Utilities for ARCO.

This module provides utilities for implementing retry and fallback mechanisms
for API calls and other operations that may fail temporarily.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retry_on_exceptions: Optional[List[type]] = None,
        retry_on_status_codes: Optional[List[int]] = None
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            backoff_factor: Multiplier for delay between retries
            retry_on_exceptions: List of exception types to retry on
            retry_on_status_codes: List of HTTP status codes to retry on
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.backoff_factor = backoff_factor
        self.retry_on_exceptions = retry_on_exceptions or [
            ConnectionError, 
            TimeoutError, 
            asyncio.TimeoutError
        ]
        self.retry_on_status_codes = retry_on_status_codes or [
            408,  # Request Timeout
            429,  # Too Many Requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504   # Gateway Timeout
        ]


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for retrying functions that may fail temporarily.
    
    Args:
        config: Retry configuration
        
    Returns:
        Decorated function with retry logic
    """
    retry_config = config or RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(1, retry_config.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Check for HTTP status code in result if it's a dict with 'status_code'
                    if isinstance(result, dict) and 'status_code' in result:
                        status_code = result.get('status_code')
                        if status_code in retry_config.retry_on_status_codes:
                            if attempt < retry_config.max_retries:
                                delay = retry_config.retry_delay * (retry_config.backoff_factor ** (attempt - 1))
                                logger.warning(
                                    f"Received status code {status_code}, retrying in {delay:.2f}s "
                                    f"(attempt {attempt}/{retry_config.max_retries})"
                                )
                                time.sleep(delay)
                                continue
                    
                    return result
                    
                except tuple(retry_config.retry_on_exceptions) as e:
                    last_exception = e
                    if attempt < retry_config.max_retries:
                        delay = retry_config.retry_delay * (retry_config.backoff_factor ** (attempt - 1))
                        logger.warning(
                            f"Operation failed with {e.__class__.__name__}: {str(e)}, "
                            f"retrying in {delay:.2f}s (attempt {attempt}/{retry_config.max_retries})"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Operation failed after {retry_config.max_retries} attempts: "
                            f"{e.__class__.__name__}: {str(e)}"
                        )
            
            if last_exception:
                raise last_exception
            
            # This should never happen, but makes the type checker happy
            raise RuntimeError("Unexpected error in retry logic")
        
        return wrapper
    
    return decorator


async def with_retry_async(
    func: Callable[..., Any],
    *args: Any,
    config: Optional[RetryConfig] = None,
    **kwargs: Any
) -> Any:
    """
    Retry an async function with exponential backoff.
    
    Args:
        func: Async function to retry
        *args: Arguments to pass to the function
        config: Retry configuration
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Result of the function call
    """
    retry_config = config or RetryConfig()
    last_exception = None
    
    for attempt in range(1, retry_config.max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            
            # Check for HTTP status code in result if it's a dict with 'status_code'
            if isinstance(result, dict) and 'status_code' in result:
                status_code = result.get('status_code')
                if status_code in retry_config.retry_on_status_codes:
                    if attempt < retry_config.max_retries:
                        delay = retry_config.retry_delay * (retry_config.backoff_factor ** (attempt - 1))
                        logger.warning(
                            f"Received status code {status_code}, retrying in {delay:.2f}s "
                            f"(attempt {attempt}/{retry_config.max_retries})"
                        )
                        await asyncio.sleep(delay)
                        continue
            
            return result
            
        except tuple(retry_config.retry_on_exceptions) as e:
            last_exception = e
            if attempt < retry_config.max_retries:
                delay = retry_config.retry_delay * (retry_config.backoff_factor ** (attempt - 1))
                logger.warning(
                    f"Operation failed with {e.__class__.__name__}: {str(e)}, "
                    f"retrying in {delay:.2f}s (attempt {attempt}/{retry_config.max_retries})"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Operation failed after {retry_config.max_retries} attempts: "
                    f"{e.__class__.__name__}: {str(e)}"
                )
    
    if last_exception:
        raise last_exception
    
    # This should never happen, but makes the type checker happy
    raise RuntimeError("Unexpected error in retry logic")


class FallbackChain:
    """
    Chain of fallback functions to try in sequence.
    
    This class allows defining a sequence of functions to try in order,
    moving to the next one if the previous one fails.
    """
    
    def __init__(self, functions: List[Callable[..., Any]]):
        """
        Initialize the fallback chain.
        
        Args:
            functions: List of functions to try in sequence
        """
        self.functions = functions
    
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the fallback chain.
        
        Args:
            *args: Arguments to pass to the functions
            **kwargs: Keyword arguments to pass to the functions
            
        Returns:
            Result of the first successful function
            
        Raises:
            Exception: If all functions fail
        """
        exceptions = []
        
        for i, func in enumerate(self.functions):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Fallback function {i+1}/{len(self.functions)} failed: {str(e)}")
                exceptions.append(e)
        
        if exceptions:
            logger.error(f"All fallback functions failed. Last error: {str(exceptions[-1])}")
            raise exceptions[-1]
        
        raise ValueError("No fallback functions provided")
    
    async def execute_async(self, *args: Any, **kwargs: Any) -> Any:
        """
        Execute the fallback chain asynchronously.
        
        Args:
            *args: Arguments to pass to the functions
            **kwargs: Keyword arguments to pass to the functions
            
        Returns:
            Result of the first successful function
            
        Raises:
            Exception: If all functions fail
        """
        exceptions = []
        
        for i, func in enumerate(self.functions):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Fallback function {i+1}/{len(self.functions)} failed: {str(e)}")
                exceptions.append(e)
        
        if exceptions:
            logger.error(f"All fallback functions failed. Last error: {str(exceptions[-1])}")
            raise exceptions[-1]
        
        raise ValueError("No fallback functions provided")