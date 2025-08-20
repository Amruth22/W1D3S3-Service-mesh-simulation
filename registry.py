"""
Service Registry - Port 8081
Simulates K8s service discovery and health monitoring
"""

import asyncio
import yaml
from datetime import datetime
from fastapi import FastAPI, HTTPException
from typing import Dict, List
import aiohttp

from models import ServiceInfo, ServiceStatus, RegistryResponse

class ServiceRegistry:
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.load_config()
    
    def load_config(self):
        """Load service configuration from deployment.yaml"""
        try:
            with open("config/deployment.yaml", "r") as file:
                config = yaml.safe_load(file)
            
            # Register services from config
            for service_key, service_config in config["services"].items():
                service_info = ServiceInfo(
                    name=service_config["name"],
                    path=service_config["path"],
                    replicas=service_config["replicas"],
                    health_check=service_config["health_check"],
                    description=service_config["description"]
                )
                self.services[service_key] = service_info
                print(f"📋 Registered service: {service_info.name} at {service_info.path}")
        
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
    
    async def check_service_health(self, service_key: str) -> bool:
        """Check health of a specific service"""
        if service_key not in self.services:
            return False
        
        service = self.services[service_key]
        health_url = f"http://localhost:8080{service.health_check}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=2)) as response:
                    if response.status == 200:
                        service.status = ServiceStatus.HEALTHY
                        service.last_health_check = datetime.now()
                        return True
                    else:
                        service.status = ServiceStatus.UNHEALTHY
                        return False
        except Exception:
            service.status = ServiceStatus.DOWN
            return False
    
    async def health_check_all_services(self):
        """Check health of all registered services"""
        print("🏥 Running health checks on all services...")
        
        for service_key in self.services.keys():
            is_healthy = await self.check_service_health(service_key)
            service = self.services[service_key]
            status_emoji = "✅" if is_healthy else "❌"
            print(f"{status_emoji} {service.name}: {service.status}")
    
    def get_service_endpoints(self) -> List[str]:
        """Get all available service endpoints"""
        endpoints = []
        for service in self.services.values():
            if service.status == ServiceStatus.HEALTHY:
                endpoints.append(f"http://localhost:8080{service.path}")
        return endpoints
    
    def get_registry_info(self) -> RegistryResponse:
        """Get complete registry information"""
        services_list = list(self.services.values())
        healthy_count = sum(1 for s in services_list if s.status == ServiceStatus.HEALTHY)
        
        return RegistryResponse(
            services=services_list,
            total_services=len(services_list),
            healthy_services=healthy_count
        )

# Create FastAPI app for registry
app = FastAPI(title="Service Registry", description="K8s Service Discovery Simulation")
registry = ServiceRegistry()

@app.on_event("startup")
async def startup_event():
    """Start background health checking"""
    print("🚀 Service Registry starting on port 8081...")
    
    # Start background health checking
    asyncio.create_task(periodic_health_check())

async def periodic_health_check():
    """Periodic health check task"""
    while True:
        await registry.health_check_all_services()
        await asyncio.sleep(30)  # Check every 30 seconds

@app.get("/")
async def root():
    """Registry root endpoint"""
    return {
        "service": "Service Registry",
        "port": 8081,
        "description": "K8s Service Discovery Simulation",
        "endpoints": {
            "services": "/services",
            "health": "/health",
            "discovery": "/discovery"
        }
    }

@app.get("/services", response_model=RegistryResponse)
async def get_services():
    """Get all registered services"""
    return registry.get_registry_info()

@app.get("/services/{service_name}")
async def get_service(service_name: str):
    """Get specific service info"""
    service = registry.services.get(service_name)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@app.get("/health")
async def registry_health():
    """Registry health check"""
    return {
        "status": "healthy",
        "service": "registry",
        "timestamp": datetime.now(),
        "registered_services": len(registry.services)
    }

@app.get("/discovery")
async def service_discovery():
    """Service discovery endpoint - returns available services"""
    endpoints = registry.get_service_endpoints()
    return {
        "available_endpoints": endpoints,
        "total_endpoints": len(endpoints),
        "timestamp": datetime.now()
    }

@app.post("/health-check")
async def trigger_health_check():
    """Manually trigger health check"""
    await registry.health_check_all_services()
    return {"message": "Health check completed", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)