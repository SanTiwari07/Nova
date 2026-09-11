import json
import os
import uuid
from typing import Dict, Any, List
from .interface import CommerceInterface
from catalog.product_repository import ProductRepository

class MockCommerceAdapter(CommerceInterface):
    def __init__(self):
        self.repo = ProductRepository()
        self.carts = {}
        self.orders = {}
                
    async def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return self.repo.search(query, skip=0, limit=10)
        
    async def get_product(self, product_id: str) -> Dict[str, Any]:
        return self.repo.get_by_id(product_id)
        
    async def check_availability(self, product_id: str) -> bool:
        p = await self.get_product(product_id)
        return p is not None and p.get("availability") == "IN_STOCK"
        
    async def compare_options(self, product_id: str) -> List[Dict[str, Any]]:
        import random
        p = await self.get_product(product_id)
        if not p:
            return []
        
        base_price = p.get("price", 100)
        pack_size = p.get("pack_size", "1 unit")
        
        providers = [
            {"id": "blinkit", "name": "Blinkit"},
            {"id": "zepto", "name": "Zepto"},
            {"id": "swiggy", "name": "Swiggy Instamart"},
            {"id": "zomato", "name": "Zomato"},
            {"id": "bigbasket", "name": "BigBasket"},
            {"id": "flipkart", "name": "Flipkart"}
        ]
        
        # Use deterministic randomness based on product id so prices stay consistent per product
        random.seed(product_id)
        
        offers = []
        for prov in providers:
            price_var = random.uniform(-0.05, 0.1)
            product_price = round(base_price * (1 + price_var))
            delivery_fee = random.choice([0, 15, 25, 30])
            service_fee = random.choice([5, 10, 15])
            discount = random.choice([0, 0, 10, 20])
            
            is_in_stock = random.random() > 0.1
            
            effective_total = product_price + delivery_fee + service_fee - discount
            
            offers.append({
                "retailerId": prov["id"],
                "retailerName": prov["name"],
                "integrationType": "Demo Integration",
                "productId": product_id,
                "productName": p.get("name"),
                "brand": p.get("brand"),
                "packSize": pack_size,
                "productPrice": product_price,
                "discount": discount,
                "deliveryFee": delivery_fee,
                "serviceFee": service_fee,
                "effectiveTotal": effective_total,
                "unitPrice": effective_total,
                "availability": "IN_STOCK" if is_in_stock else "OUT_OF_STOCK",
                "deliveryEstimate": random.choice(["10-15 min", "20-30 min", "Today", "Tomorrow"]) if is_in_stock else "Unavailable"
            })
            
        return offers
        
    async def create_cart(self) -> str:
        cart_id = f"cart_{uuid.uuid4().hex[:8]}"
        self.carts[cart_id] = []
        return cart_id
        
    async def add_to_cart(self, cart_id: str, product_id: str):
        if cart_id not in self.carts:
            raise ValueError("Invalid cart")
        p = await self.get_product(product_id)
        if p:
            self.carts[cart_id].append(p)
            
    async def checkout(self, cart_id: str) -> Dict[str, Any]:
        if cart_id not in self.carts:
            raise ValueError("Invalid cart")
            
        order_id = f"ord_{uuid.uuid4().hex[:8]}"
        order = {
            "id": order_id,
            "status": "CONFIRMED",
            "items": self.carts[cart_id],
            "total": sum(i["price"] for i in self.carts[cart_id])
        }
        self.orders[order_id] = order
        return order
    
    def get_orders(self) -> List[Dict[str, Any]]:
        return list(self.orders.values())
