from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid
import json
import os

PERSISTENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "activity_state.json")

# Seed events representing realistic recent household activity
INITIAL_SEED_EVENTS: List[Dict[str, Any]] = [
    {
        "id": "evt_seed_001",
        "type": "PURCHASE_COMPLETED",
        "title": "Milk Replenished Automatically",
        "description": "Milk was running low (~0.3L left). NOVA ordered 1L Amul Taaza.",
        "status": "COMPLETED",
        "entityType": "PRODUCT",
        "entityId": "prod_000109",
        "decision": "AUTO",
        "product": "Amul Taaza Milk 1L",
        "cost": 68,
        "reasons": [
            "Household had ~0.3 L remaining (less than 1 day's supply).",
            "Average daily consumption is ~0.6 L/day.",
            "Price ₹68 is well within autonomous safety limit (₹500).",
            "Sufficient monthly budget remaining."
        ],
        "metadata": {
            "retailer": "Swiggy Instamart",
            "order_id": "ord_sim_9104",
            "quantity": 1,
            "unit": "L",
            "savings": 0
        },
        "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=14)).isoformat()
    },
    {
        "id": "evt_seed_002",
        "type": "AUTONOMOUS_ACTION",
        "title": "Cooking Oil Check — No Action Needed",
        "description": "Evaluated cooking oil stock. Household has 2.1L remaining, enough for ~30 days.",
        "status": "INFO",
        "entityType": "PANTRY",
        "entityId": "prod_000030",
        "decision": "DO_NOTHING",
        "product": "Fortune Sunflower Oil 5L",
        "cost": 0,
        "reasons": [
            "Current stock: 2.1 L in pantry.",
            "Average consumption: 0.07 L/day (~30 days of supply remaining).",
            "NOVA applied spending restraint; no unnecessary purchase made."
        ],
        "metadata": {
            "days_remaining": 30,
            "confidence": 95
        },
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1, minutes=20)).isoformat()
    },
    {
        "id": "evt_seed_003",
        "type": "PLAN_CREATED",
        "title": "Plan Created: Maggi Tonight",
        "description": "Reconciled meal requirements against live pantry inventory.",
        "status": "COMPLETED",
        "entityType": "PLAN",
        "entityId": "plan_maggi",
        "decision": "AUTO",
        "product": "Maggi 2-Minute Masala Noodles",
        "cost": 14,
        "reasons": [
            "Cooking Oil (2.1L) and Salt (0.4kg) are already available in pantry.",
            "Maggi 2-Minute Noodles pack is missing.",
            "Prepared autonomous restock for ₹14."
        ],
        "metadata": {
            "meal": "Maggi Instant Noodles",
            "available_items": ["Cooking Oil", "Salt & Spices"],
            "missing_items": ["Maggi Noodles"]
        },
        "timestamp": (datetime.now(timezone.utc) - timedelta(hours=3, minutes=45)).isoformat()
    },
    {
        "id": "evt_seed_004",
        "type": "BUDGET_CHANGED",
        "title": "Monthly Budget Active",
        "description": "Household monthly spending envelope set to ₹3,000.",
        "status": "COMPLETED",
        "entityType": "BUDGET",
        "entityId": "budget_household",
        "decision": "AUTO",
        "product": "Household Budget",
        "cost": 0,
        "reasons": [
            "Autonomous safety ceiling configured at ₹500 per transaction.",
            "₹1,560 remaining for month after recurring essentials."
        ],
        "metadata": {
            "monthly_budget": 3000,
            "auto_limit": 500,
            "spent": 1440,
            "remaining": 1560
        },
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=1, hours=2)).isoformat()
    },
    {
        "id": "evt_seed_005",
        "type": "INVENTORY_UPDATED",
        "title": "Pantry Audit Completed",
        "description": "Tracked 12 household staples. 2 items flagged for upcoming restock.",
        "status": "INFO",
        "entityType": "PANTRY",
        "entityId": "pantry_audit",
        "decision": "DO_NOTHING",
        "product": "Pantry Inventory",
        "cost": 0,
        "reasons": [
            "Atta (1.2kg) and Basmati Rice (1.8kg) approaching reorder point.",
            "Detergent (1.2kg) and Sugar (2.5kg) in healthy comfort zone."
        ],
        "metadata": {
            "total_items": 12,
            "urgent_count": 1,
            "upcoming_count": 3
        },
        "timestamp": (datetime.now(timezone.utc) - timedelta(days=1, hours=8)).isoformat()
    }
]


class AuditService:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        """Loads events from disk or initializes with realistic seeds."""
        if "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("NOVA_TEST_MODE") == "1":
            self.logs = [dict(ev) for ev in INITIAL_SEED_EVENTS]
            return
        if os.path.exists(PERSISTENCE_PATH):
            try:
                with open(PERSISTENCE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        self.logs = data
                        return
            except Exception as e:
                print(f"[AuditService] Failed to load {PERSISTENCE_PATH}: {e}")

        # Fallback to seed events
        self.logs = [dict(ev) for ev in INITIAL_SEED_EVENTS]
        self._save()

    def _save(self):
        """Persists events to disk."""
        if "PYTEST_CURRENT_TEST" in os.environ or os.environ.get("NOVA_TEST_MODE") == "1":
            return
        try:
            os.makedirs(os.path.dirname(PERSISTENCE_PATH), exist_ok=True)
            with open(PERSISTENCE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.logs, f, indent=2)
        except Exception as e:
            print(f"[AuditService] Failed to save {PERSISTENCE_PATH}: {e}")

    def reset(self):
        """Resets to initial realistic seed state."""
        self.logs = [dict(ev) for ev in INITIAL_SEED_EVENTS]
        self._save()

    def log_event(
        self,
        event_type: str,
        title: str,
        description: str,
        entity_type: str = "PRODUCT",
        entity_id: Optional[str] = None,
        product: Optional[str] = None,
        decision: Optional[str] = None,
        reasons: Optional[List[str]] = None,
        cost: float = 0.0,
        status: str = "COMPLETED",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Creates and prepends a rich ActivityEvent."""
        event = {
            "id": f"evt_{uuid.uuid4().hex[:8]}",
            "type": event_type,
            "title": title,
            "description": description,
            "status": status,
            "entityType": entity_type,
            "entityId": entity_id or "",
            "product": product or title,
            "decision": decision or "AUTO",
            "cost": float(cost),
            "reasons": reasons or [],
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.logs.insert(0, event)
        # Cap to 200 recent events
        if len(self.logs) > 200:
            self.logs = self.logs[:200]
        self._save()
        return event

    def log_decision(self, product_name: str, decision: str, reasons: List[str]):
        """Legacy compatibility wrapper that creates a structured ActivityEvent."""
        decision_titles = {
            "AUTO": f"Taken care of: {product_name}",
            "ASK": f"Needs your review: {product_name}",
            "DO_NOTHING": f"All sorted: {product_name}",
            "BLOCKED": f"Restricted by rules: {product_name}",
            "WAIT": f"Waiting for better price: {product_name}",
            "CHECKOUT_COMPLETED": f"Order placed for {product_name}",
            "POLICY_UPDATED": f"Policy updated: {product_name}",
            "BUDGET_UPDATED": f"Budget updated: {product_name}",
            "PANTRY_UPDATED": f"Pantry updated: {product_name}",
            "REMINDER_CREATED": f"Reminder scheduled: {product_name}",
        }
        title = decision_titles.get(decision, f"Decision on {product_name}")
        desc = reasons[0] if reasons else f"NOVA processed decision: {decision}"

        event_type = "DECISION_MADE"
        if decision == "AUTO":
            event_type = "PURCHASE_COMPLETED"
        elif decision == "DO_NOTHING":
            event_type = "AUTONOMOUS_ACTION"
        elif decision == "ASK":
            event_type = "PURCHASE_WAITING_APPROVAL"
        elif decision == "BLOCKED":
            event_type = "PURCHASE_BLOCKED"
        elif decision == "BUDGET_UPDATED":
            event_type = "BUDGET_CHANGED"
        elif decision == "PANTRY_UPDATED":
            event_type = "INVENTORY_UPDATED"

        self.log_event(
            event_type=event_type,
            title=title,
            description=desc,
            entity_type="PRODUCT",
            product=product_name,
            decision=decision,
            reasons=reasons,
            status="PENDING" if decision == "ASK" else "COMPLETED"
        )

    def get_recent(self, limit: int = 50, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns recent activity events, optionally filtered."""
        if filter_type and filter_type != "ALL":
            return [l for l in self.logs if l.get("type") == filter_type or l.get("decision") == filter_type][:limit]
        return self.logs[:limit]
