from typing import Dict, Any, List, Optional

class InventoryService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Mock pantry state for the demo
        # Seeded state matching the exact demo scenarios
        self.pantry = {
            "prod_000109": {
                "name": "Amul Taaza Milk 1L",
                "image": None,
                "quantity": 0.3,
                "unit": "L",
                "daily_consumption": 0.6,
                "status": "LOW",
                "category": "Milk"
            },
            "prod_000030": {
                "name": "Fortune Sunflower Oil 5L",
                "image": None,
                "quantity": 2.1,
                "unit": "L",
                "daily_consumption": 0.07,
                "status": "HEALTHY",
                "category": "Oil"
            },
            "prod_000010": {
                "name": "India Gate Basmati Rice 5kg",
                "image": None,
                "quantity": 1.8,
                "unit": "kg",
                "daily_consumption": 0.25,
                "status": "LOW",
                "category": "Rice"
            },
            "prod_000001": {
                "name": "Aashirvaad Whole Wheat Atta 5kg",
                "image": None,
                "quantity": 1.2,
                "unit": "kg",
                "daily_consumption": 0.2,
                "status": "LOW",
                "category": "Atta"
            },
            "prod_000050": {
                "name": "Tata Salt 1kg",
                "image": None,
                "quantity": 0.4,
                "unit": "kg",
                "daily_consumption": 0.02,
                "status": "LOW",
                "category": "Salt"
            },
            "prod_000060": {
                "name": "Tata Sampann Toor Dal 1kg",
                "image": None,
                "quantity": 0.5,
                "unit": "kg",
                "daily_consumption": 0.07,
                "status": "LOW",
                "category": "Dal"
            },
            "prod_000080": {
                "name": "Tata Tea Gold 500g",
                "image": None,
                "quantity": 0.15,
                "unit": "kg",
                "daily_consumption": 0.025,
                "status": "LOW",
                "category": "Tea"
            },
            "prod_000090": {
                "name": "Surf Excel Matic Front Load Detergent 2kg",
                "image": None,
                "quantity": 1.2,
                "unit": "kg",
                "daily_consumption": 0.08,
                "status": "HEALTHY",
                "category": "Detergent"
            },
            "prod_000070": {
                "name": "Madhur Pure & Hygienic Sugar 5kg",
                "image": None,
                "quantity": 1.8,
                "unit": "kg",
                "daily_consumption": 0.1,
                "status": "HEALTHY",
                "category": "Sugar"
            },
            "prod_000100": {
                "name": "Dettol Original Soap Pack of 4",
                "image": None,
                "quantity": 1.0,
                "unit": "pack",
                "daily_consumption": 0.03,
                "status": "LOW",
                "category": "Soap"
            },
            "prod_000110": {
                "name": "Harpic Power Plus Toilet Cleaner 1L",
                "image": None,
                "quantity": 0.4,
                "unit": "bottle",
                "daily_consumption": 0.025,
                "status": "LOW",
                "category": "Cleaning"
            },
            "prod_000120": {
                "name": "Head & Shoulders Shampoo 340ml",
                "image": None,
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
            confidence = data.get("confidence")
            if confidence is None:
                if "milk" in data["name"].lower() or data["status"] == "LOW":
                    confidence = 0.92
                elif "oil" in data["name"].lower():
                    confidence = 0.88
                else:
                    confidence = 0.85
            items.append({
                "product_id": pid,
                "name": data["name"],
                "image": data.get("image", ""),
                "quantity": data["quantity"],
                "unit": data["unit"],
                "days_remaining": round(days_rem, 1),
                "status": data["status"],
                "category": data["category"],
                "confidence": confidence,
                "confidence_score": f"{int(confidence * 100)}%"
            })
        return items

    def get_item(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self.pantry.get(product_id)

    def get_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Look up pantry item by product ID, name substring, or category."""
        target = name.lower().strip()
        for pid, data in self.pantry.items():
            if target == pid.lower() or target in data["name"].lower() or target in data.get("category", "").lower():
                return data
        return None
        
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
        # Find existing by name or category
        for existing_id, data in self.pantry.items():
            if (name and data.get("name", "").lower() == name.lower()) or (category and data.get("category", "").lower() == category.lower()):
                data["quantity"] += quantity
                data["status"] = "HEALTHY"
                return
        
        # If not existing in pantry, add as new item
        pid = f"prod_added_{len(self.pantry) + 1}"
        new_qty = float(quantity) if quantity else 1.0
        self.pantry[pid] = {
            "name": name.title() if name else (category.title() if category else "Item"),
            "quantity": new_qty,
            "unit": unit or "units",
            "daily_consumption": max(0.05, round(new_qty / 14, 3)),
            "status": "HEALTHY",
            "category": category.title() if category else "General",
            "confidence": 0.90
        }
        
    def update_item(self, item_name_or_id: str, quantity: Optional[float] = None, unit: Optional[str] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """Update existing item or add new pantry item."""
        target_item = None
        target_pid = None
        key_lower = item_name_or_id.lower().strip()

        # Try match by ID
        if item_name_or_id in self.pantry:
            target_pid = item_name_or_id
            target_item = self.pantry[item_name_or_id]
        else:
            # Try match by name or category
            for pid, data in self.pantry.items():
                if key_lower in data["name"].lower() or key_lower in data["category"].lower() or data["name"].lower() in key_lower:
                    target_pid = pid
                    target_item = data
                    break

        if target_item:
            if quantity is not None:
                target_item["quantity"] = float(quantity)
            if unit:
                target_item["unit"] = unit
            if status:
                target_item["status"] = status
            elif quantity is not None:
                target_item["status"] = "LOW" if quantity <= 0.2 else "HEALTHY"
            return {"product_id": target_pid, **target_item}
        else:
            # Create new pantry item
            new_pid = f"prod_custom_{len(self.pantry) + 1}"
            new_qty = float(quantity) if quantity is not None else 1.0
            new_status = status or ("LOW" if new_qty <= 0.2 else "HEALTHY")
            self.pantry[new_pid] = {
                "name": item_name_or_id.title(),
                "quantity": new_qty,
                "unit": unit or "units",
                "daily_consumption": max(0.05, round(new_qty / 14, 3)),
                "status": new_status,
                "category": "Pantry",
                "confidence": 0.88
            }
            return {"product_id": new_pid, **self.pantry[new_pid]}

    def report_depleted(self, item_name: str) -> Dict[str, Any]:
        """Mark an item in the pantry as depleted/empty."""
        return self.update_item(item_name, quantity=0.0, status="LOW")
