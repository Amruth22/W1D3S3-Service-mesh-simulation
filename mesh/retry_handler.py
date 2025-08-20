"""
Simple Retry Handler - Service Mesh Component
Implements retry logic with exponential backoff
"""

import asyncio
import random
from typing import Callable, Any

class RetryHandler:
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
    
    async def retry_call(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """
        Retry a function call with exponential backoff
        """
        last_exception = None
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                print(f"🔄 Attempt {attempt}/{self.max_attempts} for {service_name}")
                result = await func(*args, **kwargs)
                
                if attempt > 1:
                    print(f"✅ {service_name} succeeded on attempt {attempt}")
                
                return result
                
            except Exception as e:
                last_exception = e
                print(f"❌ {service_name} failed on attempt {attempt}: {str(e)}")
                
                # Don't wait after the last attempt
                if attempt < self.max_attempts:
                    # Exponential backoff with jitter
                    delay = self.base_delay * (2 ** (attempt - 1))
                    jitter = random.uniform(0, 0.1)  # Add small random delay
                    total_delay = delay + jitter
                    
                    print(f"⏳ Waiting {total_delay:.2f}s before retry...")
                    await asyncio.sleep(total_delay)
        
        # All attempts failed
        print(f"💥 All {self.max_attempts} attempts failed for {service_name}")
        raise last_exception
    
    def should_retry(self, exception: Exception) -> bool:
        """
        Determine if an exception should trigger a retry
        """
        # Simple logic - retry on most exceptions except specific ones
        error_message = str(exception).lower()
        
        # Don't retry on these errors
        non_retryable = [
            "not found",
            "unauthorized", 
            "forbidden",
            "bad request"
        ]
        
        for non_retry in non_retryable:
            if non_retry in error_message:
                return False
        
        return True