"""
Main Gateway Server - Port 8080
Simulates K8s Ingress Controller + Service Mesh
Routes traffic to different services based on URL paths
"""

import asyncio
import random
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# Import our services
from services.catalog_service import CatalogService
from services.cart_service import CartService
from services.order_service import OrderService

# Import service mesh components
from mesh.circuit_breaker import CircuitBreakerManager
from mesh.retry_handler import RetryHandler

class ServiceMeshGateway:
    def __init__(self):
        # Initialize services (simulating pods)
        self.catalog_service = CatalogService()
        self.cart_service = CartService()
        self.order_service = OrderService()
        
        # Initialize service mesh components
        self.circuit_breaker = CircuitBreakerManager()
        self.retry_handler = RetryHandler(max_attempts=3, base_delay=1.0)
        
        print("[GATEWAY] Service Mesh Gateway initialized")
        print("[GATEWAY] Services loaded: catalog, cart, order")
    
    async def call_with_mesh(self, service_name: str, service_func, *args, **kwargs):
        """
        Call service through service mesh (circuit breaker + retry)
        """
        try:
            # First try with circuit breaker
            result = await self.circuit_breaker.call_service(
                service_name, service_func, *args, **kwargs
            )
            return result
            
        except Exception as e:
            # If circuit breaker allows, try with retry logic
            if "Circuit breaker OPEN" not in str(e):
                try:
                    result = await self.retry_handler.retry_call(
                        service_name, service_func, *args, **kwargs
                    )
                    return result
                except Exception as retry_error:
                    raise retry_error
            else:
                raise e
    
    def simulate_load_balancing(self):
        """Simulate load balancing with random delays"""
        # Simulate different response times from different "replicas"
        delay = random.uniform(0.01, 0.1)
        replica_id = random.randint(1, 3)
        return delay, replica_id

# Create FastAPI app
app = FastAPI(
    title="Service Mesh Gateway", 
    description="K8s Ingress + Service Mesh Simulation"
)

# Initialize gateway
gateway = ServiceMeshGateway()

@app.middleware("http")
async def add_mesh_headers(request: Request, call_next):
    """Add service mesh headers to responses"""
    # Simulate load balancing
    delay, replica_id = gateway.simulate_load_balancing()
    await asyncio.sleep(delay)
    
    response = await call_next(request)
    
    # Add mesh headers
    response.headers["X-Service-Mesh"] = "enabled"
    response.headers["X-Replica-ID"] = str(replica_id)
    response.headers["X-Response-Time"] = f"{delay:.3f}s"
    
    return response

# Root endpoint
@app.get("/")
async def root():
    """Gateway root endpoint"""
    return {
        "service": "Service Mesh Gateway",
        "port": 8080,
        "description": "K8s Ingress Controller + Service Mesh Simulation",
        "services": {
            "catalog": "/catalog/*",
            "cart": "/cart/*", 
            "order": "/order/*"
        },
        "mesh_features": [
            "Circuit Breaker",
            "Retry Logic", 
            "Load Balancing",
            "Health Monitoring"
        ]
    }

# Service Mesh Status
@app.get("/mesh/status")
async def mesh_status():
    """Get service mesh status"""
    return {
        "circuit_breakers": gateway.circuit_breaker.get_status(),
        "timestamp": datetime.now(),
        "gateway_status": "healthy"
    }

@app.post("/mesh/reset/{service_name}")
async def reset_circuit_breaker(service_name: str):
    """Reset circuit breaker for a service"""
    success = gateway.circuit_breaker.reset_breaker(service_name)
    if success:
        return {"message": f"Circuit breaker reset for {service_name}"}
    else:
        raise HTTPException(status_code=404, detail="Service not found")

# =============================================================================
# CATALOG SERVICE ROUTES (/catalog/*)
# =============================================================================

@app.get("/catalog/health")
async def catalog_health():
    """Catalog service health check"""
    try:
        result = await gateway.call_with_mesh(
            "catalog", gateway.catalog_service.health_check
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/catalog/products")
async def get_products():
    """Get all products from catalog"""
    try:
        result = await gateway.call_with_mesh(
            "catalog", gateway.catalog_service.get_products
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/catalog/products/{product_id}")
async def get_product(product_id: int):
    """Get specific product"""
    try:
        result = await gateway.call_with_mesh(
            "catalog", gateway.catalog_service.get_product, product_id
        )
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/catalog/search")
async def search_products(q: str):
    """Search products"""
    try:
        result = await gateway.call_with_mesh(
            "catalog", gateway.catalog_service.search_products, q
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# =============================================================================
# CART SERVICE ROUTES (/cart/*)
# =============================================================================

@app.get("/cart/health")
async def cart_health():
    """Cart service health check"""
    try:
        result = await gateway.call_with_mesh(
            "cart", gateway.cart_service.health_check
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/cart/{user_id}")
async def get_cart(user_id: str):
    """Get user's cart"""
    try:
        result = await gateway.call_with_mesh(
            "cart", gateway.cart_service.get_cart, user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/cart/{user_id}/add")
async def add_to_cart(user_id: str, product_id: int, quantity: int = 1):
    """Add item to cart"""
    try:
        result = await gateway.call_with_mesh(
            "cart", gateway.cart_service.add_to_cart, user_id, product_id, quantity
        )
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=503, detail=str(e))

@app.delete("/cart/{user_id}/remove/{product_id}")
async def remove_from_cart(user_id: str, product_id: int):
    """Remove item from cart"""
    try:
        result = await gateway.call_with_mesh(
            "cart", gateway.cart_service.remove_from_cart, user_id, product_id
        )
        return result
    except Exception as e:
        if "not found" in str(e).lower() or "not in cart" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=503, detail=str(e))

@app.delete("/cart/{user_id}/clear")
async def clear_cart(user_id: str):
    """Clear user's cart"""
    try:
        result = await gateway.call_with_mesh(
            "cart", gateway.cart_service.clear_cart, user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# =============================================================================
# ORDER SERVICE ROUTES (/order/*)
# =============================================================================

@app.get("/order/health")
async def order_health():
    """Order service health check"""
    try:
        result = await gateway.call_with_mesh(
            "order", gateway.order_service.health_check
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.post("/order/create")
async def create_order(user_id: str):
    """Create order from user's cart"""
    try:
        # First get cart items (inter-service communication)
        cart_result = await gateway.call_with_mesh(
            "cart", gateway.cart_service.get_cart, user_id
        )
        
        if not cart_result["items"]:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Create order
        order_result = await gateway.call_with_mesh(
            "order", gateway.order_service.create_order, user_id, cart_result["items"]
        )
        
        # Clear cart after successful order
        await gateway.call_with_mesh(
            "cart", gateway.cart_service.clear_cart, user_id
        )
        
        return order_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/order/{order_id}")
async def get_order(order_id: str):
    """Get order details"""
    try:
        result = await gateway.call_with_mesh(
            "order", gateway.order_service.get_order, order_id
        )
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/order/user/{user_id}")
async def get_user_orders(user_id: str):
    """Get all orders for a user"""
    try:
        result = await gateway.call_with_mesh(
            "order", gateway.order_service.get_user_orders, user_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)