import json
import os
from typing import Dict, Any

PERSISTENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "budget_state.json")

DEMO_DEFAULTS = {
    "monthly_budget": 5500.0,
    "spent": 3940.0,
    "auto_limit": 500.0,
    "currency": "INR",
}


class BudgetService:
    def __init__(self):
        self.reset()

    def reset(self):
        """Restore demo defaults, then overlay any persisted values."""
        self.monthly_budget: float = DEMO_DEFAULTS["monthly_budget"]
        self.spent: float = DEMO_DEFAULTS["spent"]
        self.auto_limit: float = DEMO_DEFAULTS["auto_limit"]
        self.currency: str = DEMO_DEFAULTS["currency"]
        self._load_persisted()

    # ── Persistence ─────────────────────────────────────────────────────────

    def _load_persisted(self):
        try:
            if os.path.exists(PERSISTENCE_PATH):
                with open(PERSISTENCE_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self.monthly_budget = float(saved.get("monthly_budget", self.monthly_budget))
                self.spent = float(saved.get("spent", self.spent))
                self.auto_limit = float(saved.get("auto_limit", self.auto_limit))
                self.currency = saved.get("currency", self.currency)
        except Exception:
            pass

    def _persist(self):
        try:
            os.makedirs(os.path.dirname(PERSISTENCE_PATH), exist_ok=True)
            with open(PERSISTENCE_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "monthly_budget": self.monthly_budget,
                    "spent": self.spent,
                    "auto_limit": self.auto_limit,
                    "currency": self.currency,
                }, f, indent=2)
        except Exception:
            pass

    # ── Mutations ────────────────────────────────────────────────────────────

    def set_budget(self, amount: float):
        self.monthly_budget = float(amount)
        self._persist()

    def set_auto_limit(self, amount: float):
        self.auto_limit = float(amount)
        self._persist()

    async def record_spend(self, amount: float):
        self.spent = round(self.spent + float(amount), 2)
        self._persist()

    # ── Reads ────────────────────────────────────────────────────────────────

    async def get_remaining_budget(self) -> float:
        return round(self.monthly_budget - self.spent, 2)

    async def get_auto_buy_limit(self) -> float:
        return self.auto_limit

    def get_status(self) -> Dict[str, Any]:
        remaining = round(self.monthly_budget - self.spent, 2)
        spent_pct = round((self.spent / self.monthly_budget) * 100, 1) if self.monthly_budget > 0 else 0
        return {
            "monthly": self.monthly_budget,
            "spent": self.spent,
            "remaining": remaining,
            "auto_limit": self.auto_limit,
            "currency": self.currency,
            "spent_pct": spent_pct,
            "pressure": spent_pct > 90,
        }

    def get_forecast(self, upcoming_spend: float = 0.0) -> Dict[str, Any]:
        """
        Return a budget forecast given an estimated upcoming spend.
        upcoming_spend is calculated by the caller from pantry replenishment estimates.
        """
        remaining = self.monthly_budget - self.spent
        projected_total = self.spent + upcoming_spend
        projected_remaining = self.monthly_budget - projected_total
        over_budget = projected_total > self.monthly_budget
        return {
            "spent": round(self.spent, 2),
            "remaining": round(remaining, 2),
            "estimated_upcoming": round(upcoming_spend, 2),
            "projected_total": round(projected_total, 2),
            "projected_remaining": round(projected_remaining, 2),
            "over_budget": over_budget,
            "shortfall": round(projected_total - self.monthly_budget, 2) if over_budget else 0,
            "monthly": self.monthly_budget,
            "auto_limit": self.auto_limit,
        }
