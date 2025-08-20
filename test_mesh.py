#!/usr/bin/env python3
"""
Simple test script to demonstrate K8s Service Mesh simulation
Tests all services and mesh features
"""

import requests
import time
import json

GATEWAY_URL = "http://localhost:8080"
REGISTRY_URL = "http://localhost:8081"

def test_service_mesh():
    """Test the service mesh simulation"""
    print("🧪 Testing K8s Service Mesh Simulation")
    print("=" * 60)
    
    try:
        # Test 1: Gateway Health
        print("\n1. 🌐 Testing Gateway")
        response = requests.get(f"{GATEWAY_URL}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Gateway: {data['service']}")
            print(f"Services: {', '.join(data['services'].keys())}")
        
        # Test 2: Service Registry
        print("\n2. 📋 Testing Service Registry")
        response = requests.get(f"{REGISTRY_URL}/services")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Services: {data['total_services']}")
            print(f"Healthy Services: {data['healthy_services']}")
        
        # Test 3: Catalog Service
        print("\n3. 📦 Testing Catalog Service")
        response = requests.get(f"{GATEWAY_URL}/catalog/products")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Products found: {data['total']}")
            print(f"Service: {data['service']}")
        
        # Test 4: Cart Service
        print("\n4. 🛒 Testing Cart Service")
        user_id = "test_user"
        
        # Get empty cart
        response = requests.get(f"{GATEWAY_URL}/cart/{user_id}")
        print(f"Get Cart Status: {response.status_code}")
        
        # Add item to cart
        response = requests.post(f"{GATEWAY_URL}/cart/{user_id}/add?product_id=1&quantity=2")
        print(f"Add to Cart Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Added: {data['item']['name']} x{data['item']['quantity']}")
        
        # Test 5: Order Service
        print("\n5. 📋 Testing Order Service")
        response = requests.post(f"{GATEWAY_URL}/order/create?user_id={user_id}")
        print(f"Create Order Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Order ID: {data['order_id']}")
            print(f"Total: ${data['total']}")
        
        # Test 6: Service Mesh Status
        print("\n6. 🕸️  Testing Service Mesh Status")
        response = requests.get(f"{GATEWAY_URL}/mesh/status")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Circuit Breakers:")
            for service, status in data['circuit_breakers'].items():
                print(f"  {service}: {status['state']} (failures: {status['failure_count']})")
        
        # Test 7: Health Checks
        print("\n7. 🏥 Testing Health Checks")
        services = ["catalog", "cart", "order"]
        for service in services:
            response = requests.get(f"{GATEWAY_URL}/{service}/health")
            print(f"{service.capitalize()} Health: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Status: {data['status']}")
        
        # Test 8: Service Discovery
        print("\n8. 🔍 Testing Service Discovery")
        response = requests.get(f"{REGISTRY_URL}/discovery")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available Endpoints: {data['total_endpoints']}")
            for endpoint in data['available_endpoints']:
                print(f"  {endpoint}")
        
        # Test 9: Circuit Breaker (Simulate Failures)
        print("\n9. ⚡ Testing Circuit Breaker")
        print("Triggering multiple failures to test circuit breaker...")
        
        for i in range(5):
            try:
                # This should fail and trigger circuit breaker
                response = requests.get(f"{GATEWAY_URL}/catalog/products/999", timeout=1)
                print(f"Attempt {i+1}: {response.status_code}")
            except Exception as e:
                print(f"Attempt {i+1}: Failed - {str(e)[:50]}")
            time.sleep(0.5)
        
        # Check circuit breaker status
        response = requests.get(f"{GATEWAY_URL}/mesh/status")
        if response.status_code == 200:
            data = response.json()
            catalog_status = data['circuit_breakers'].get('catalog', {})
            print(f"Catalog Circuit Breaker: {catalog_status.get('state', 'unknown')}")
        
        # Test 10: Load Balancing (Check Headers)
        print("\n10. ⚖️  Testing Load Balancing")
        replicas = set()
        for i in range(5):
            response = requests.get(f"{GATEWAY_URL}/catalog/products")
            if 'X-Replica-ID' in response.headers:
                replicas.add(response.headers['X-Replica-ID'])
                response_time = response.headers.get('X-Response-Time', 'unknown')
                print(f"Request {i+1}: Replica {response.headers['X-Replica-ID']}, Time: {response_time}")
        
        print(f"Used {len(replicas)} different replicas")
        
        print("\n" + "=" * 60)
        print("✅ Service Mesh Testing Complete!")
        print("🎓 K8s concepts demonstrated:")
        print("  • Service Discovery (Registry)")
        print("  • Path-based Routing (Ingress)")
        print("  • Circuit Breaker (Fault Tolerance)")
        print("  • Load Balancing (Traffic Distribution)")
        print("  • Health Monitoring (Liveness Probes)")
        print("  • Inter-service Communication")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to services")
        print("Make sure both services are running:")
        print("  python start_services.py")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

def main():
    """Main function"""
    print("Starting Service Mesh tests...")
    print("Make sure services are running on ports 8080 and 8081")
    print()
    
    test_service_mesh()

if __name__ == "__main__":
    main()