"""
Simple Cart Service - Simulates a shopping cart microservice
"""

import random
import asyncio
from datetime import datetime
from models import HealthResponse
from typing import Dict, List

class CartService:
    def __init__(self):
        self.name = "cart-service"
        # Simple in-memory cart storage
        self.carts: Dict[str, List] = {}
    
    async def health_check(self):
        """Health check endpoint"""
        # Simulate random failures (8% chance)
        if random.random() < 0.08:
            return HealthResponse(
                service=self.name,
                status="unhealthy",
                timestamp=datetime.now(),
                message="Cart service overloaded"
            )
        
        return HealthResponse(
            service=self.name,
            status="healthy",
            timestamp=datetime.now()
        )
    
    async def get_cart(self, user_id: str):
        """Get user's cart"""
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # Get or create cart
        cart_items = self.carts.get(user_id, [])
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)
        
        return {
            "user_id": user_id,
            "items": cart_items,
            "total": round(total, 2),
            "item_count": len(cart_items),
            "service": self.name
        }
    
    async def add_to_cart(self, user_id: str, product_id: int, quantity: int = 1):
        """Add item to cart"""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Simulate random failures (3% chance)
        if random.random() < 0.03:
            raise Exception("Failed to add item to cart")
        
        # Initialize cart if doesn't exist
        if user_id not in self.carts:
            self.carts[user_id] = []
        
        # Simple product info (in real app, would call catalog service)
        product_info = {
            1: {"name": "Laptop", "price": 999.99},
            2: {"name": "Phone", "price": 599.99},
            3: {"name": "Book", "price": 19.99},
            4: {"name": "Headphones", "price": 149.99},
            5: {"name": "Shoes", "price": 79.99}
        }
        
        product = product_info.get(product_id)
        if not product:
            raise Exception(f"Product {product_id} not found")
        
        # Add to cart
        cart_item = {
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        }
        
        self.carts[user_id].append(cart_item)
        
        return {
            "message": "Item added to cart",
            "user_id": user_id,
            "item": cart_item,
            "service": self.name
        }
    
    async def remove_from_cart(self, user_id: str, product_id: int):
        """Remove item from cart"""
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        if user_id not in self.carts:
            raise Exception("Cart not found")
        
        # Remove item
        original_length = len(self.carts[user_id])
        self.carts[user_id] = [
            item for item in self.carts[user_id] 
            if item["product_id"] != product_id
        ]
        
        if len(self.carts[user_id]) == original_length:
            raise Exception(f"Product {product_id} not in cart")
        
        return {
            "message": "Item removed from cart",
            "user_id": user_id,
            "product_id": product_id,
            "service": self.name
        }
    
    async def clear_cart(self, user_id: str):
        """Clear user's cart"""
        await asyncio.sleep(random.uniform(0.02, 0.1))
        
        if user_id in self.carts:
            del self.carts[user_id]
        
        return {
            "message": "Cart cleared",
            "user_id": user_id,
            "service": self.name
        }