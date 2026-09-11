from typing import Dict, Any, List

class InventoryService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Mock pantry state for the demo
        # Seeded state matching the exact demo scenarios
        self.pantry = {
            "prod_000109": {
                "name": "Amul Taaza Milk 1L",
                "quantity": 0.3,
                "unit": "L",
                "daily_consumption": 0.6,
                "status": "LOW",
                "category": "Milk"
            },
            "prod_000030": {
                "name": "Fortune Sunflower Oil 5L",
                "quantity": 2.1,
                "unit": "L",
                "daily_consumption": 0.07,
                "status": "HEALTHY",
                "category": "Oil"
            },
            "prod_000010": {
                "name": "India Gate Basmati Rice 5kg",
                "quantity": 1.8,
                "unit": "kg",
                "daily_consumption": 0.25,
                "status": "LOW",
                "category": "Rice"
            },
            "prod_000001": {
                "name": "Aashirvaad Whole Wheat Atta 5kg",
                "quantity": 1.2,
                "unit": "kg",
                "daily_consumption": 0.2,
                "status": "LOW",
                "category": "Atta"
            },
            "prod_000050": {
                "name": "Tata Salt 1kg",
                "quantity": 0.4,
                "unit": "kg",
                "daily_consumption": 0.02,
                "status": "LOW",
                "category": "Salt"
            },
            "prod_000060": {
                "name": "Tata Sampann Toor Dal 1kg",
                "quantity": 0.5,
                "unit": "kg",
                "daily_consumption": 0.07,
                "status": "LOW",
                "category": "Dal"
            },
            "prod_000080": {
                "name": "Tata Chai Classic Tea 500g",
                "quantity": 0.15,
                "unit": "kg",
                "daily_consumption": 0.025,
                "status": "LOW",
                "category": "Tea"
            },
            "prod_000090": {
                "name": "Surf Excel Detergent 3kg",
                "quantity": 1.2,
                "unit": "kg",
                "daily_consumption": 0.08,
                "status": "HEALTHY",
                "category": "Detergent"
            },
            "prod_000070": {
                "name": "Uttam Sugar 5kg",
                "quantity": 1.8,
                "unit": "kg",
                "daily_consumption": 0.1,
                "status": "HEALTHY",
                "category": "Sugar"
            },
            "prod_000100": {
                "name": "Dettol Original Soap",
                "quantity": 1.0,
                "unit": "pack",
                "daily_consumption": 0.03,
                "status": "LOW",
                "category": "Soap"
            },
            "prod_000110": {
                "name": "Harpic Power Plus 750ml",
                "quantity": 0.4,
                "unit": "bottle",
                "daily_consumption": 0.025,
                "status": "LOW",
                "category": "Cleaning"
            },
            "prod_000120": {
                "name": "Head & Shoulders Shampoo 340ml",
                "quantity": 0.1,
                "unit": "bottle",
                "daily_consumption": 0.025,
                "status": "LOW",
                "category": "Hair Care"
            },
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
