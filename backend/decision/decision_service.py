from typing import Dict, Any, Tuple, List

class DecisionEngine:
    def __init__(self, budget_service, policy_service, inventory_service, session_service):
        self.budget_service = budget_service
        self.policy_service = policy_service
        self.inventory_service = inventory_service
        self.session_service = session_service
        
    async def evaluate(self, product: Dict[str, Any], context: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Returns one of: AUTO, ASK, WAIT, DO_NOTHING, BLOCKED
        and a list of reasons.
        """
        reasons = []
        category = product.get("category", "")
        price = product.get("price", 0)
        
        # 1. Policy check - Restricted
        is_allowed = await self.policy_service.is_category_allowed(category)
        if not is_allowed:
            reasons.append("Category is restricted by your rules.")
            return "BLOCKED", reasons
            
        # 2. Inventory check
        needs_replenishment = await self.inventory_service.needs_replenishment(category)
        if not needs_replenishment:
            reasons.append("You still have enough inventory.")
            return "DO_NOTHING", reasons
        reasons.append("Inventory was low or missing.")
            
        # 3. Policy check - Ask Required
        requires_ask = await self.policy_service.requires_ask(category)
        if requires_ask:
            reasons.append("This category requires your explicit approval.")
            return "ASK", reasons
            
        # 4. Budget check
        auto_limit = await self.budget_service.get_auto_buy_limit()
        if price > auto_limit:
            reasons.append(f"Price exceeds automatic buy limit of ₹{auto_limit}.")
            return "ASK", reasons
            
        budget_remaining = await self.budget_service.get_remaining_budget()
        if price > budget_remaining:
            reasons.append(f"Insufficient remaining budget (₹{budget_remaining}).")
            return "ASK", reasons
        reasons.append("Price was within budget and auto-buy limits.")
            
        # 5. Confidence check
        confidence = context.get("confidence", "HIGH")
        if confidence == "LOW":
            reasons.append("NOVA had low confidence in predicting this need.")
            return "ASK", reasons
        reasons.append("High confidence prediction.")
        
        # 6. Autonomy Mode check
        if self.session_service.autonomy_profile != "FULL_AUTOPILOT":
            reasons.append(f"Autonomous mode is OFF (Profile: {self.session_service.autonomy_profile}).")
            return "ASK", reasons
        
        reasons.append("Your rules allowed the purchase.")
        return "AUTO", reasons
