"""
Simple Catalog Service - Simulates a product catalog microservice
"""

import random
import asyncio
from datetime import datetime
from models import HealthResponse, ProductResponse

class CatalogService:
    def __init__(self):
        self.name = "catalog-service"
        self.products = [
            {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
            {"id": 2, "name": "Phone", "price": 599.99, "category": "Electronics"},
            {"id": 3, "name": "Book", "price": 19.99, "category": "Books"},
            {"id": 4, "name": "Headphones", "price": 149.99, "category": "Electronics"},
            {"id": 5, "name": "Shoes", "price": 79.99, "category": "Fashion"}
        ]
    
    async def health_check(self):
        """Health check endpoint"""
        # Simulate random failures (10% chance)
        if random.random() < 0.1:
            return HealthResponse(
                service=self.name,
                status="unhealthy",
                timestamp=datetime.now(),
                message="Service temporarily unavailable"
            )
        
        return HealthResponse(
            service=self.name,
            status="healthy",
            timestamp=datetime.now()
        )
    
    async def get_products(self):
        """Get all products"""
        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Simulate random failures (5% chance)
        if random.random() < 0.05:
            raise Exception("Database connection failed")
        
        return {
            "products": self.products,
            "total": len(self.products),
            "service": self.name
        }
    
    async def get_product(self, product_id: int):
        """Get specific product"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # Find product
        product = next((p for p in self.products if p["id"] == product_id), None)
        if not product:
            raise Exception(f"Product {product_id} not found")
        
        return {
            "product": product,
            "service": self.name
        }
    
    async def search_products(self, query: str):
        """Search products"""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Simple search
        results = [
            p for p in self.products 
            if query.lower() in p["name"].lower() or query.lower() in p["category"].lower()
        ]
        
        return {
            "products": results,
            "query": query,
            "total": len(results),
            "service": self.name
        }