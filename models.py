"""
Simple data models for K8s simulation
"""

from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DOWN = "down"

class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# Service Registry Models
class ServiceInfo(BaseModel):
    name: str
    path: str
    replicas: int
    health_check: str
    description: str
    status: ServiceStatus = ServiceStatus.HEALTHY
    last_health_check: datetime = datetime.now()

class RegistryResponse(BaseModel):
    services: List[ServiceInfo]
    total_services: int
    healthy_services: int

# Circuit Breaker Models
class CircuitBreaker(BaseModel):
    service_name: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    failure_threshold: int = 3
    timeout_seconds: int = 30

# API Response Models
class HealthResponse(BaseModel):
    service: str
    status: str
    timestamp: datetime
    message: str = "Service is running"

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str

class CartResponse(BaseModel):
    user_id: str
    items: List[Dict]
    total: float

class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    items: List[Dict]
    total: float
    status: str