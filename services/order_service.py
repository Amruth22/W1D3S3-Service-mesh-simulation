"""
Simple Order Service - Simulates an order processing microservice
"""

import random
import asyncio
import uuid
from datetime import datetime
from models import HealthResponse
from typing import Dict, List

class OrderService:
    def __init__(self):
        self.name = "order-service"
        # Simple in-memory order storage
        self.orders: Dict[str, Dict] = {}
    
    async def health_check(self):
        """Health check endpoint"""
        # Simulate random failures (12% chance - highest failure rate)
        if random.random() < 0.12:
            return HealthResponse(
                service=self.name,
                status="unhealthy",
                timestamp=datetime.now(),
                message="Order processing system down"
            )
        
        return HealthResponse(
            service=self.name,
            status="healthy",
            timestamp=datetime.now()
        )
    
    async def create_order(self, user_id: str, items: List[Dict]):
        """Create new order"""
        await asyncio.sleep(random.uniform(0.2, 0.8))  # Longer processing time
        
        # Simulate random failures (7% chance)
        if random.random() < 0.07:
            raise Exception("Payment processing failed")
        
        # Generate order ID
        order_id = str(uuid.uuid4())[:8]
        
        # Calculate total
        total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        # Create order
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "items": items,
            "total": round(total, 2),
            "status": "confirmed",
            "created_at": datetime.now().isoformat(),
            "service": self.name
        }
        
        self.orders[order_id] = order
        
        return order
    
    async def get_order(self, order_id: str):
        """Get order details"""
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        order = self.orders.get(order_id)
        if not order:
            raise Exception(f"Order {order_id} not found")
        
        return order
    
    async def get_user_orders(self, user_id: str):
        """Get all orders for a user"""
        await asyncio.sleep(random.uniform(0.15, 0.4))
        
        user_orders = [
            order for order in self.orders.values() 
            if order["user_id"] == user_id
        ]
        
        return {
            "user_id": user_id,
            "orders": user_orders,
            "total_orders": len(user_orders),
            "service": self.name
        }
    
    async def update_order_status(self, order_id: str, status: str):
        """Update order status"""
        await asyncio.sleep(random.uniform(0.1, 0.2))
        
        if order_id not in self.orders:
            raise Exception(f"Order {order_id} not found")
        
        valid_statuses = ["confirmed", "processing", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise Exception(f"Invalid status: {status}")
        
        self.orders[order_id]["status"] = status
        self.orders[order_id]["updated_at"] = datetime.now().isoformat()
        
        return {
            "order_id": order_id,
            "status": status,
            "message": "Order status updated",
            "service": self.name
        }
    
    async def cancel_order(self, order_id: str):
        """Cancel an order"""
        await asyncio.sleep(random.uniform(0.2, 0.5))
        
        if order_id not in self.orders:
            raise Exception(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        if order["status"] in ["shipped", "delivered"]:
            raise Exception("Cannot cancel shipped or delivered order")
        
        self.orders[order_id]["status"] = "cancelled"
        self.orders[order_id]["cancelled_at"] = datetime.now().isoformat()
        
        return {
            "order_id": order_id,
            "message": "Order cancelled successfully",
            "service": self.name
        }