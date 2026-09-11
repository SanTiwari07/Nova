from typing import Dict, Any, List

class InventoryService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Mock pantry state for the demo
        # Seeded state matching the exact demo scenarios
        self.pantry = {
            "prod_000109": { # We assume this is some Milk (Amul Taaza Milk 1L)
                "name": "Amul Taaza Milk 1L",
                "quantity": 0.3,
                "unit": "L",
                "daily_consumption": 0.6,
                "status": "LOW",
                "category": "Milk"
            },
            "prod_000030": { # We assume this is some Oil
                "name": "Fortune Sunflower Oil 5L",
                "quantity": 2.1,
                "unit": "L",
                "daily_consumption": 0.14,
                "status": "HEALTHY",
                "category": "Oil"
            },
            "prod_000010": {
                "name": "India Gate Basmati Rice 5kg",
                "quantity": 3.8,
                "unit": "kg",
                "daily_consumption": 0.3,
                "status": "HEALTHY",
                "category": "Rice"
            }
        }
        
    def get_all(self) -> List[Dict[str, Any]]:
        items = []
        for pid, data in self.pantry.items():
            days_rem = data["quantity"] / data["daily_consumption"] if data["daily_consumption"] > 0 else 99
            items.append({
                "product_id": pid,
                "name": data["name"],
                "quantity": data["quantity"],
                "unit": data["unit"],
                "days_remaining": round(days_rem, 1),
                "status": data["status"],
                "category": data["category"]
            })
        return items
        
    async def needs_replenishment(self, product_category: str) -> bool:
        # Determine based on category for the mock scenarios since exact ID might vary
        cat = product_category.lower() if product_category else ""
        
        # If it's Maggi / Noodles, we don't have it, so yes.
        if "noodle" in cat or "maggi" in cat:
            return True
            
        # Check if we have this category
        for data in self.pantry.values():
            if data["category"].lower() in cat or cat in data["category"].lower():
                return data["status"] == "LOW"
                
        # If not in pantry, assume we need it
        return True

    def add_to_pantry(self, category: str, name: str, quantity: float, unit: str):
        # Find existing or add new
        pid = f"prod_added_{len(self.pantry)}"
        for existing_id, data in self.pantry.items():
            if data["category"].lower() == category.lower():
                data["quantity"] += quantity
                data["status"] = "HEALTHY"
                return
        
        self.pantry[pid] = {
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "daily_consumption": quantity / 10, # guess
            "status": "HEALTHY",
            "category": category
        }
