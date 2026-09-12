from typing import Dict, Any, List
from .provider_interface import AIProvider

class FallbackProvider(AIProvider):
    
    async def understand_intent(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback for intent understanding."""
        req_lower = user_request.lower()
        if "maggi" in req_lower or "noodle" in req_lower:
            return {
                "intent_type": "MEAL_PREPARATION",
                "confidence": 0.95,
                "goal": "prepare_maggi",
                "time_context": "tonight",
                "requires_inventory_check": True
            }
        elif "milk" in req_lower:
            return {
                "intent_type": "REPLENISHMENT",
                "confidence": 0.95,
                "goal": "replenish_milk",
                "time_context": "now",
                "requires_inventory_check": True
            }
        elif "harpic" in req_lower or "clean" in req_lower:
            return {
                "intent_type": "REPLENISHMENT",
                "confidence": 0.95,
                "goal": "replenish_harpic",
                "time_context": "now",
                "requires_inventory_check": True
            }
        
        return {
            "intent_type": "GENERAL_ORDER",
            "confidence": 0.8,
            "goal": req_lower.strip(),
            "time_context": "now",
            "requires_inventory_check": True
        }
        
    async def generate_response(self, user_request: str, decision: str, evidence: Dict[str, Any]) -> str:
        """Rule-based fallback response generation."""
        items = evidence.get("items", [])
        item_name = items[0].get("product", "item") if items else "item"
        
        if decision == "AUTO":
            return f"Ordered {item_name} via Swiggy Instamart (10-15 min delivery). It was missing from pantry and within auto-buy limits."
        elif decision == "ASK":
            return f"I located {item_name} on Swiggy Instamart, but this category or price requires your approval."
        elif decision == "DO_NOTHING":
            return f"You already have enough {item_name} in your household inventory."
        elif decision == "BLOCKED":
            return f"Unable to proceed with {item_name} due to policy restrictions."
        return "I can help with that, but I need a little more information."
        
    async def generate_requirements(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rule-based fallback requirements."""
        goal = intent.get("goal", "")
        if goal == "prepare_maggi":
            return [{"query": "Maggi", "quantity": 1}]
        elif goal == "replenish_milk":
            return [{"query": "Milk", "quantity": 1}]
        elif goal == "replenish_harpic":
            return [{"query": "Harpic", "quantity": 1}]
        elif goal:
            return [{"query": goal, "quantity": 1}]
        return []
