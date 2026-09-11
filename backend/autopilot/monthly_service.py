from typing import Dict, Any, List
from amazon.history_service import MockAmazonHistoryProvider
from amazon.price_service import PriceService


class MonthlyAutopilotService:
    """
    Generates the monthly household Amazon shopping plan.
    Combines purchase history, inventory estimates, budget, and policy
    to produce a NOVA Cart with per-item decisions.
    """

    def __init__(self, budget_service, policy_service, inventory_service):
        self.budget = budget_service
        self.policy = policy_service
        self.inventory = inventory_service
        self.history = MockAmazonHistoryProvider()
        self.price_service = PriceService()

    async def generate_monthly_plan(self) -> Dict[str, Any]:
        recurring = self.history.get_recurring_products()
        budget_remaining = await self.budget.get_remaining_budget()
        auto_limit = await self.budget.get_auto_buy_limit()

        items = []
        total_estimated = 0
        approval_required = []
        auto_items = []

        for product in recurring:
            days_until = product.get("days_until_needed", 30)
            current_price = product.get("current_price", 0)
            avg_price = product.get("avg_price", current_price)
            confidence = product.get("confidence", 0.8)
            category = product.get("category", "")

            # Skip items not needed this month
            if days_until > 20:
                continue

            price_pct_above = ((current_price - avg_price) / avg_price) * 100 if avg_price else 0
            price_rec = self.price_service.get_price_recommendation(product["product_id"])

            # Determine decision
            if not await self.policy.is_category_allowed(category):
                decision = "BLOCKED"
                reason = "Category is restricted by your rules."
            elif days_until > 10 and price_pct_above > 8:
                decision = "WAIT"
                reason = f"Price is {price_pct_above:.0f}% above average. You have {days_until} days remaining. Wait for a better price."
            elif current_price > auto_limit:
                decision = "ASK"
                reason = f"Price ₹{current_price} exceeds your auto-buy limit of ₹{auto_limit}."
            elif confidence < 0.7:
                decision = "ASK"
                reason = "NOVA confidence is low for this purchase."
            else:
                decision = "AUTO"
                reason = f"Recurring purchase. Expected within {days_until} days. Price is within limits."

            item = {
                **product,
                "decision": decision,
                "reason": reason,
                "requires_approval": decision == "ASK",
                "price_pct_vs_avg": round(price_pct_above, 1),
                "quantity": product.get("typical_quantity", 1),
                "estimated_cost": current_price * product.get("typical_quantity", 1),
            }
            items.append(item)

            if decision in ("AUTO", "WAIT"):
                auto_items.append(item)
                total_estimated += item["estimated_cost"]
            elif decision == "ASK":
                approval_required.append(item)
                total_estimated += item["estimated_cost"]

        monthly_budget = self.budget.monthly_budget
        savings_opportunities = self._find_savings(items)

        return {
            "month": "September 2026",
            "items": items,
            "auto_items": auto_items,
            "approval_required": approval_required,
            "total_estimated": total_estimated,
            "monthly_budget": monthly_budget,
            "budget_remaining_after": monthly_budget - self.budget.spent - total_estimated,
            "savings_opportunities": savings_opportunities,
            "stats": {
                "total_items": len(items),
                "auto_count": len([i for i in items if i["decision"] == "AUTO"]),
                "ask_count": len(approval_required),
                "wait_count": len([i for i in items if i["decision"] == "WAIT"]),
                "blocked_count": len([i for i in items if i["decision"] == "BLOCKED"]),
            },
            "source": "AMAZON_MOCK",
        }

    def _find_savings(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        savings = []
        for item in items:
            if item.get("price_pct_vs_avg", 0) > 5:
                savings.append({
                    "product_id": item["product_id"],
                    "name": item["name"],
                    "type": "PRICE_HIGH",
                    "message": f"Current price is {item['price_pct_vs_avg']}% above average. Consider waiting.",
                    "potential_saving": round((item["current_price"] - item["avg_price"]) * item.get("typical_quantity", 1), 0),
                })
        return savings
