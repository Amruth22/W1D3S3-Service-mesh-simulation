"""
Simple Circuit Breaker - Service Mesh Component
Protects services from cascading failures
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict
from models import CircuitBreaker, CircuitState

class CircuitBreakerManager:
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.failure_threshold = 3
        self.timeout_seconds = 30
    
    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(
                service_name=service_name,
                failure_threshold=self.failure_threshold,
                timeout_seconds=self.timeout_seconds
            )
        return self.breakers[service_name]
    
    async def call_service(self, service_name: str, service_func, *args, **kwargs):
        """Call service through circuit breaker"""
        breaker = self.get_breaker(service_name)
        
        # Check if circuit is open
        if breaker.state == CircuitState.OPEN:
            if self._should_attempt_reset(breaker):
                breaker.state = CircuitState.HALF_OPEN
                print(f"[CIRCUIT] Circuit breaker for {service_name} is HALF-OPEN (testing)")
            else:
                raise Exception(f"Circuit breaker OPEN for {service_name} - service unavailable")
        
        try:
            # Call the service
            result = await service_func(*args, **kwargs)
            
            # Success - reset failure count
            if breaker.state == CircuitState.HALF_OPEN:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                print(f"[CIRCUIT] Circuit breaker for {service_name} is CLOSED (recovered)")
            elif breaker.state == CircuitState.CLOSED:
                breaker.failure_count = 0
            
            return result
            
        except Exception as e:
            # Failure - increment count
            breaker.failure_count += 1
            breaker.last_failure_time = datetime.now()
            
            print(f"[CIRCUIT] Service {service_name} failed ({breaker.failure_count}/{breaker.failure_threshold}): {str(e)}")
            
            # Open circuit if threshold reached
            if breaker.failure_count >= breaker.failure_threshold:
                breaker.state = CircuitState.OPEN
                print(f"[CIRCUIT] Circuit breaker OPENED for {service_name} - too many failures!")
            
            raise e
    
    def _should_attempt_reset(self, breaker: CircuitBreaker) -> bool:
        """Check if enough time has passed to attempt reset"""
        if not breaker.last_failure_time:
            return True
        
        time_since_failure = datetime.now() - breaker.last_failure_time
        return time_since_failure > timedelta(seconds=breaker.timeout_seconds)
    
    def get_status(self) -> Dict:
        """Get status of all circuit breakers"""
        status = {}
        for service_name, breaker in self.breakers.items():
            status[service_name] = {
                "state": breaker.state,
                "failure_count": breaker.failure_count,
                "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None
            }
        return status
    
    def reset_breaker(self, service_name: str):
        """Manually reset a circuit breaker"""
        if service_name in self.breakers:
            breaker = self.breakers[service_name]
            breaker.state = CircuitState.CLOSED
            breaker.failure_count = 0
            breaker.last_failure_time = None
            print(f"[CIRCUIT] Circuit breaker for {service_name} manually reset")
            return True
        return False