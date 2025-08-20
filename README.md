# K8s Service Mesh Simulation

A **simple Python simulation** of Kubernetes concepts and Service Mesh using only **2 ports** - perfect for learning K8s without actual containers!

## 🎯 **Learning Objectives**

This project simulates:
- **Kubernetes Pods** → Path-based routing (`/catalog/*`, `/cart/*`, `/order/*`)
- **Kubernetes Services** → Service registry and discovery
- **Kubernetes Deployments** → YAML configuration files
- **Kubernetes Ingress** → Gateway routing on port 8080
- **Service Mesh** → Circuit breaker, retry logic, load balancing
- **Inter-service Communication** → Services calling each other

## 🏗️ **Architecture**

```
Port 8080 (Gateway)          Port 8081 (Registry)
┌─────────────────────┐      ┌─────────────────────┐
│   Service Mesh      │      │  Service Discovery  │
│   Gateway           │◄────►│  & Health Monitor   │
│                     │      │                     │
│ /catalog/* ────────►│      │ • Service Registry  │
│ /cart/*    ────────►│      │ • Health Checks     │
│ /order/*   ────────►│      │ • Config Management │
└─────────────────────┘      └─────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              Virtual Microservices                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │   Catalog   │ │    Cart     │ │    Order    │   │
│  │   Service   │ │   Service   │ │   Service   │   │
│  └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### 1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 2. **Start Services**
```bash
python start_services.py
```

This starts:
- **Gateway** (Port 8080) - Service mesh with routing
- **Registry** (Port 8081) - Service discovery

### 3. **Run Unit Tests**
```bash
python unit_test.py
```

### 4. **Access Services**
- **Gateway API**: http://localhost:8080
- **Service Registry**: http://localhost:8081
- **API Documentation**: http://localhost:8080/docs

## 📁 **Project Structure**

```
├── gateway.py              # Main gateway (port 8080)
├── registry.py            # Service registry (port 8081)
├── start_services.py      # Start both services
├── unit_test.py          # Core 5 unit tests
├── config/
│   └── deployment.yaml    # Service configuration
├── services/
│   ├── catalog_service.py # Product catalog
│   ├── cart_service.py    # Shopping cart
│   └── order_service.py   # Order processing
├── mesh/
│   ├── circuit_breaker.py # Circuit breaker logic
│   └── retry_handler.py   # Retry with backoff
└── models.py             # Data models
```

## 🛍️ **Use Case: Online Shopping System**

### **Three Virtual Microservices:**

#### 1. **Catalog Service** (`/catalog/*`)
- `GET /catalog/products` - List all products
- `GET /catalog/products/{id}` - Get specific product
- `GET /catalog/search?q=query` - Search products
- `GET /catalog/health` - Health check

#### 2. **Cart Service** (`/cart/*`)
- `GET /cart/{user_id}` - Get user's cart
- `POST /cart/{user_id}/add` - Add item to cart
- `DELETE /cart/{user_id}/remove/{product_id}` - Remove item
- `DELETE /cart/{user_id}/clear` - Clear cart
- `GET /cart/health` - Health check

#### 3. **Order Service** (`/order/*`)
- `POST /order/create?user_id=X` - Create order from cart
- `GET /order/{order_id}` - Get order details
- `GET /order/user/{user_id}` - Get user's orders
- `GET /order/health` - Health check

## 🕸️ **Service Mesh Features**

### **1. Circuit Breaker**
- **Threshold**: 3 failures = circuit opens
- **Timeout**: 30 seconds before retry
- **States**: CLOSED → OPEN → HALF_OPEN

```bash
# Check circuit breaker status
curl http://localhost:8080/mesh/status

# Reset circuit breaker
curl -X POST http://localhost:8080/mesh/reset/catalog
```

### **2. Retry Logic**
- **Max Attempts**: 3 retries
- **Backoff**: Exponential (1s, 2s, 4s)
- **Smart Retry**: Doesn't retry on 404, 401, etc.

### **3. Load Balancing**
- **Strategy**: Simulated with random delays
- **Headers**: `X-Replica-ID`, `X-Response-Time`
- **Replicas**: Configured in `deployment.yaml`

### **4. Health Monitoring**
- **Automatic**: Every 30 seconds
- **Manual**: `POST /health-check` on registry
- **Status**: healthy, unhealthy, down

## 🔧 **Configuration**

Edit `config/deployment.yaml` to modify:

```yaml
services:
  catalog:
    name: "catalog-service"
    path: "/catalog"
    replicas: 2
    health_check: "/catalog/health"
    
mesh:
  circuit_breaker:
    failure_threshold: 3
    timeout_seconds: 30
  retry:
    max_attempts: 3
    backoff_seconds: 1
```

## 🧪 **Unit Testing**

### **Core 5 Tests**
The `unit_test.py` includes focused tests for:

1. **Gateway Test** - Path-based routing (K8s Ingress)
2. **Registry Test** - Service discovery functionality  
3. **Microservice Test** - Inter-service communication
4. **Circuit Breaker Test** - Fault tolerance mechanisms
5. **Mesh Status Test** - Service mesh observability

### **Run Tests**
```bash
# Start services first
python start_services.py

# Run unit tests (in another terminal)
python unit_test.py
```

## 🧪 **Manual Testing Scenarios**

### **1. Normal Operations**
```bash
# Get products
curl http://localhost:8080/catalog/products

# Add to cart
curl -X POST "http://localhost:8080/cart/user123/add?product_id=1&quantity=2"

# Create order
curl -X POST http://localhost:8080/order/create?user_id=user123
```

### **2. Circuit Breaker Testing**
```bash
# Trigger failures (try invalid product ID multiple times)
for i in {1..5}; do
  curl http://localhost:8080/catalog/products/999
done

# Check circuit breaker status
curl http://localhost:8080/mesh/status
```

### **3. Service Discovery**
```bash
# Get available services
curl http://localhost:8081/discovery

# Get service registry
curl http://localhost:8081/services
```

## 📊 **Monitoring**

### **Service Registry Dashboard**
```bash
curl http://localhost:8081/services
```

### **Circuit Breaker Status**
```bash
curl http://localhost:8080/mesh/status
```

### **Health Checks**
```bash
curl http://localhost:8080/catalog/health
curl http://localhost:8080/cart/health
curl http://localhost:8080/order/health
```

## 🎓 **Educational Value**

### **K8s Concepts Learned:**
1. **Pods** → Services running on different paths
2. **Services** → Service registry and discovery
3. **Deployments** → YAML configuration
4. **Ingress** → Path-based routing
5. **ConfigMaps** → Configuration management
6. **Liveness Probes** → Health checks

### **Service Mesh Concepts:**
1. **Traffic Management** → Load balancing, routing
2. **Fault Tolerance** → Circuit breaker, retries
3. **Observability** → Health monitoring, headers
4. **Service Discovery** → Registry-based discovery

## 🔍 **How It Works**

### **Path-Based Routing (Simulates K8s Services)**
```
http://localhost:8080/catalog/products  → Catalog Service
http://localhost:8080/cart/user123      → Cart Service  
http://localhost:8080/order/create      → Order Service
```

### **Service Registry (Simulates K8s DNS)**
- Services register themselves with health status
- Gateway discovers services through registry
- Health checks monitor service availability

### **Inter-Service Communication**
```python
# Order service calls Cart service
cart_result = await gateway.call_with_mesh(
    "cart", gateway.cart_service.get_cart, user_id
)
```

## 🚀 **Next Steps**

To extend this simulation:
1. Add authentication/authorization
2. Implement distributed tracing
3. Add metrics collection
4. Create a web dashboard
5. Add more service mesh features
6. Implement blue-green deployments

## 🤝 **Perfect for Learning**

This simulation is ideal for:
- **Students** learning Kubernetes concepts
- **Developers** understanding service mesh
- **Teams** practicing microservices patterns
- **Anyone** wanting to learn without complex setup

---

**No Docker, No K8s, Just Pure Python Learning! 🐍**