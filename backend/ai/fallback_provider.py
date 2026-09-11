from typing import Dict, Any, List
from .provider_interface import AIProvider

class FallbackProvider(AIProvider):
    
    async def understand_intent(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based fallback for intent understanding."""
        req_lower = user_request.lower()
        if "maggi" in req_lower:
            return {
                "intent_type": "MEAL_PREPARATION",
                "confidence": 0.5,
                "goal": "prepare_maggi",
                "time_context": "tonight",
                "requires_inventory_check": True
            }
        
        return {
            "intent_type": "UNKNOWN",
            "confidence": 0.0,
            "goal": "unknown",
            "time_context": "now",
            "requires_inventory_check": False
        }
        
    async def generate_response(self, user_request: str, decision: str, evidence: Dict[str, Any]) -> str:
        """Rule-based fallback response generation."""
        if decision == "AUTO":
            return "Taken care of."
        elif decision == "ASK":
            return "Needs your input. Could you review this?"
        elif decision == "DO_NOTHING":
            return "No action needed at this time."
        elif decision == "BLOCKED":
            return "I couldn't do this due to your current rules."
        return "I can help with that, but I need a little more information."
        
    async def generate_requirements(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rule-based fallback requirements."""
        if intent.get("goal") == "prepare_maggi":
            return [{"query": "Maggi noodles", "quantity": 1}]
        return []
