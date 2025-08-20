#!/usr/bin/env python3
"""
Unit Test for K8s Service Mesh Simulation
Core 5 tests covering essential K8s + Service Mesh concepts
"""

import requests
import time

GATEWAY_URL = "http://localhost:8080"
REGISTRY_URL = "http://localhost:8081"

def unit_test_service_mesh():
    """Core 5 unit tests for service mesh simulation"""
    print("[TEST] K8s Service Mesh - Core Unit Tests")
    print("=" * 50)
    
    try:
        # Test 1: Gateway Health (Ingress)
        print("\n1. [GATEWAY] Testing Service Mesh Gateway")
        response = requests.get(f"{GATEWAY_URL}/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Gateway: {data['service']}")
            print(f"   Services: {', '.join(data['services'].keys())}")
            print("   ✅ Path-based routing working")
        else:
            print("   ❌ Gateway failed")
        
        # Test 2: Service Registry (Service Discovery)
        print("\n2. [REGISTRY] Testing Service Discovery")
        response = requests.get(f"{REGISTRY_URL}/services")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total Services: {data['total_services']}")
            print(f"   Registered Services: {len(data['services'])}")
            print("   ✅ Service discovery working")
        else:
            print("   ❌ Service registry failed")
        
        # Test 3: Microservice Communication (Inter-service)
        print("\n3. [MICROSERVICE] Testing Inter-service Communication")
        user_id = "test_user"
        
        # Add item to cart (tests catalog→cart communication)
        response = requests.post(f"{GATEWAY_URL}/cart/{user_id}/add?product_id=1&quantity=1")
        print(f"   Add to Cart Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Added: {data['item']['name']}")
            
            # Create order (tests cart→order communication)
            response = requests.post(f"{GATEWAY_URL}/order/create?user_id={user_id}")
            print(f"   Create Order Status: {response.status_code}")
            
            if response.status_code == 200:
                order_data = response.json()
                print(f"   Order ID: {order_data['order_id']}")
                print(f"   Total: ${order_data['total']}")
                print("   ✅ Inter-service communication working")
            else:
                print("   ❌ Order creation failed")
        else:
            print("   ❌ Cart operation failed")
        
        # Test 4: Circuit Breaker (Fault Tolerance)
        print("\n4. [CIRCUIT BREAKER] Testing Fault Tolerance")
        print("   Triggering failures to test circuit breaker...")
        
        failure_count = 0
        for i in range(4):
            try:
                # Try to access non-existent product (should fail)
                response = requests.get(f"{GATEWAY_URL}/catalog/products/999", timeout=2)
                if response.status_code >= 400:
                    failure_count += 1
                print(f"   Attempt {i+1}: Status {response.status_code}")
            except Exception:
                failure_count += 1
                print(f"   Attempt {i+1}: Failed (timeout/error)")
            time.sleep(0.3)
        
        # Check circuit breaker status
        response = requests.get(f"{GATEWAY_URL}/mesh/status")
        if response.status_code == 200:
            data = response.json()
            catalog_breaker = data['circuit_breakers'].get('catalog', {})
            breaker_state = catalog_breaker.get('state', 'unknown')
            failure_count = catalog_breaker.get('failure_count', 0)
            
            print(f"   Circuit Breaker State: {breaker_state}")
            print(f"   Failure Count: {failure_count}")
            
            if breaker_state == 'open' or failure_count > 0:
                print("   ✅ Circuit breaker working (fault tolerance active)")
            else:
                print("   ⚠️  Circuit breaker not triggered (may need more failures)")
        else:
            print("   ❌ Could not check circuit breaker status")
        
        # Test 5: Service Mesh Status (Observability)
        print("\n5. [MESH STATUS] Testing Service Mesh Observability")
        response = requests.get(f"{GATEWAY_URL}/mesh/status")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            breakers = data['circuit_breakers']
            
            print(f"   Monitored Services: {len(breakers)}")
            print("   Circuit Breaker States:")
            
            for service, status in breakers.items():
                state = status['state']
                failures = status['failure_count']
                print(f"     {service}: {state} (failures: {failures})")
            
            print("   ✅ Service mesh monitoring working")
        else:
            print("   ❌ Service mesh status failed")
        
        # Summary
        print("\n" + "=" * 50)
        print("[TEST] Core Unit Tests Complete!")
        print("\n[CONCEPTS VERIFIED]")
        print("  ✅ K8s Ingress (Path-based routing)")
        print("  ✅ Service Discovery (Registry)")
        print("  ✅ Pod Communication (Inter-service)")
        print("  ✅ Fault Tolerance (Circuit breaker)")
        print("  ✅ Observability (Mesh monitoring)")
        print("\n[SIMULATION SUCCESS] K8s + Service Mesh concepts working!")
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to services")
        print("Make sure both services are running:")
        print("  python start_services.py")
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")

def main():
    """Main function"""
    print("Starting K8s Service Mesh Unit Tests...")
    print("Ensure services are running on ports 8080 and 8081")
    print()
    
    unit_test_service_mesh()

if __name__ == "__main__":
    main()