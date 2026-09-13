from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import os

PERSISTENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pantry_state.json")

# ─── Seeded demo household — single source of truth for inventory ─────────────
DEMO_PANTRY: Dict[str, Dict[str, Any]] = {
    "prod_000109": {
        "name": "Amul Taaza Milk 1L",
        "image": None,
        "quantity": 0.3,
        "unit": "L",
        "daily_consumption": 0.6,
        "status": "LOW",
        "category": "Milk",
        "preferred": True,
        "last_updated": None,  # filled on init
    },
    "prod_000030": {
        "name": "Fortune Sunflower Oil 5L",
        "image": None,
        "quantity": 2.1,
        "unit": "L",
        "daily_consumption": 0.07,
        "status": "HEALTHY",
        "category": "Oil",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000010": {
        "name": "India Gate Basmati Rice 5kg",
        "image": None,
        "quantity": 1.8,
        "unit": "kg",
        "daily_consumption": 0.25,
        "status": "LOW",
        "category": "Rice",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000001": {
        "name": "Aashirvaad Whole Wheat Atta 5kg",
        "image": None,
        "quantity": 1.2,
        "unit": "kg",
        "daily_consumption": 0.2,
        "status": "LOW",
        "category": "Atta",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000050": {
        "name": "Tata Salt 1kg",
        "image": None,
        "quantity": 0.4,
        "unit": "kg",
        "daily_consumption": 0.02,
        "status": "LOW",
        "category": "Salt",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000060": {
        "name": "Tata Sampann Toor Dal 1kg",
        "image": None,
        "quantity": 0.5,
        "unit": "kg",
        "daily_consumption": 0.07,
        "status": "LOW",
        "category": "Dal",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000080": {
        "name": "Tata Tea Gold 500g",
        "image": None,
        "quantity": 0.15,
        "unit": "kg",
        "daily_consumption": 0.025,
        "status": "LOW",
        "category": "Tea",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000090": {
        "name": "Surf Excel Matic Front Load Detergent 2kg",
        "image": None,
        "quantity": 1.2,
        "unit": "kg",
        "daily_consumption": 0.08,
        "status": "HEALTHY",
        "category": "Detergent",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000070": {
        "name": "Madhur Pure & Hygienic Sugar 5kg",
        "image": None,
        "quantity": 1.8,
        "unit": "kg",
        "daily_consumption": 0.1,
        "status": "HEALTHY",
        "category": "Sugar",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000100": {
        "name": "Dettol Original Soap Pack of 4",
        "image": None,
        "quantity": 1.0,
        "unit": "pack",
        "daily_consumption": 0.03,
        "status": "LOW",
        "category": "Soap",
        "preferred": True,
        "last_updated": None,
    },
    "prod_000110": {
        "name": "Harpic Power Plus Toilet Cleaner 1L",
        "image": None,
        "quantity": 0.4,
        "unit": "bottle",
        "daily_consumption": 0.025,
        "status": "LOW",
        "category": "Cleaning",
        "preferred": False,
        "last_updated": None,
    },
    "prod_000120": {
        "name": "Head & Shoulders Shampoo 340ml",
        "image": None,
        "quantity": 0.1,
        "unit": "bottle",
        "daily_consumption": 0.025,
        "status": "LOW",
        "category": "Hair Care",
        "preferred": False,
        "last_updated": None,
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compute_confidence(data: Dict[str, Any]) -> float:
    """
    Compute a real confidence score from data signals:
    - How recently was the item updated?
    - Is consumption rate defined?
    - Is quantity above zero?
    - Is the item preferred (tracked regularly)?
    """
    score = 0.7  # baseline

    # Data freshness: penalise if last_updated is old / missing
    last_upd = data.get("last_updated")
    if last_upd:
        try:
            upd_dt = datetime.fromisoformat(last_upd.replace("Z", "+00:00"))
            now_dt = datetime.now(timezone.utc)
            hours_ago = (now_dt - upd_dt).total_seconds() / 3600
            if hours_ago < 1:
                score += 0.15   # very fresh
            elif hours_ago < 24:
                score += 0.10
            elif hours_ago < 72:
                score += 0.05
            else:
                score -= 0.10   # stale
        except (ValueError, TypeError):
            score -= 0.05
    else:
        score -= 0.05  # no timestamp — less certain

    # Preferred / regularly tracked items get a bonus
    if data.get("preferred", False):
        score += 0.08

    # Penalise uncertainty when quantity is very low (harder to estimate)
    qty = data.get("quantity", 0)
    if qty <= 0:
        score -= 0.10  # depleted — very uncertain
    elif qty < 0.1:
        score -= 0.05

    # Consumption rate defined
    if data.get("daily_consumption", 0) > 0:
        score += 0.05

    return round(min(0.98, max(0.30, score)), 2)


def _compute_days_remaining(data: Dict[str, Any]) -> float:
    dcr = data.get("daily_consumption", 0)
    qty = data.get("quantity", 0)
    if dcr <= 0:
        return 99.0
    return round(qty / dcr, 1)


def _compute_urgency(days: float, confidence: float) -> str:
    """URGENT (<= 2 days), UPCOMING (2–7 days), COMFORTABLE (7+ days), UNCERTAIN (low confidence)."""
    if confidence < 0.55:
        return "UNCERTAIN"
    if days <= 2:
        return "URGENT"
    if days <= 7:
        return "UPCOMING"
    return "COMFORTABLE"


class InventoryService:
    def __init__(self):
        self.reset()

    def reset(self):
        """Restore demo seed — tries to load from persisted JSON first."""
        import copy
        self.pantry: Dict[str, Dict[str, Any]] = copy.deepcopy(DEMO_PANTRY)
        # Stamp all items with current time if no timestamp
        now = _now_iso()
        for data in self.pantry.values():
            if data.get("last_updated") is None:
                data["last_updated"] = now
        # Try load persisted overrides (preserves quantities from a running session)
        self._load_persisted()

    # ── Persistence ────────────────────────────────────────────────────────────

    def _load_persisted(self):
        try:
            if os.path.exists(PERSISTENCE_PATH):
                with open(PERSISTENCE_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                # Merge saved quantities/statuses on top of seed data
                for pid, saved_data in saved.items():
                    if pid in self.pantry:
                        self.pantry[pid].update(saved_data)
                    else:
                        self.pantry[pid] = saved_data
        except Exception:
            pass  # If persistence fails, continue with seed data

    def _persist(self):
        try:
            os.makedirs(os.path.dirname(PERSISTENCE_PATH), exist_ok=True)
            with open(PERSISTENCE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.pantry, f, indent=2)
        except Exception:
            pass

    # ── Public read API ────────────────────────────────────────────────────────

    def get_all(self) -> List[Dict[str, Any]]:
        items = []
        for pid, data in self.pantry.items():
            days_rem = _compute_days_remaining(data)
            confidence = _compute_confidence(data)
            urgency = _compute_urgency(days_rem, confidence)

            # Derive status from real days remaining
            derived_status = "LOW" if days_rem <= 3 else "HEALTHY"
            data["status"] = derived_status

            items.append({
                "product_id": pid,
                "name": data["name"],
                "image": data.get("image", ""),
                "quantity": round(data["quantity"], 2),
                "unit": data["unit"],
                "daily_consumption": data.get("daily_consumption", 0),
                "days_remaining": days_rem,
                "status": derived_status,
                "urgency": urgency,
                "category": data["category"],
                "confidence": confidence,
                "confidence_score": f"{int(confidence * 100)}%",
                "confidence_level": "High" if confidence >= 0.85 else "Moderate" if confidence >= 0.65 else "Low",
                "preferred": data.get("preferred", False),
                "last_updated": data.get("last_updated"),
            })
        return items

    def get_urgency_grouped(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return pantry items grouped by urgency for the home page."""
        all_items = self.get_all()
        groups: Dict[str, List] = {"URGENT": [], "UPCOMING": [], "COMFORTABLE": [], "UNCERTAIN": []}
        for item in all_items:
            groups[item.get("urgency", "COMFORTABLE")].append(item)
        return groups

    def get_item(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self.pantry.get(product_id)

    def get_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Look up pantry item by product ID, name substring, or category."""
        target = name.lower().strip()
        for pid, data in self.pantry.items():
            if (
                target == pid.lower()
                or target in data["name"].lower()
                or target in data.get("category", "").lower()
            ):
                return data
        return None

    def get_item_full(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """Full enriched item dict (same shape as get_all() rows)."""
        all_items = self.get_all()
        target = name_or_id.lower().strip()
        for item in all_items:
            if (
                target == item["product_id"].lower()
                or target in item["name"].lower()
                or target in item["category"].lower()
            ):
                return item
        return None

    async def needs_replenishment(self, product_category: str) -> bool:
        cat = product_category.lower() if product_category else ""

        # Maggi / noodles are not in pantry by default
        if "noodle" in cat or "maggi" in cat or "instant" in cat:
            return True

        for data in self.pantry.values():
            if (
                data["category"].lower() in cat
                or cat in data["category"].lower()
            ):
                days = _compute_days_remaining(data)
                return days <= 3  # needs replenishment if ≤ 3 days left

        # Item not in pantry at all — treat as needed
        return True

    # ── Mutations ─────────────────────────────────────────────────────────────

    def add_to_pantry(self, category: str, name: str, quantity: float, unit: str):
        now = _now_iso()
        for existing_id, data in self.pantry.items():
            if (name and data.get("name", "").lower() == name.lower()) or (
                category and data.get("category", "").lower() == category.lower()
            ):
                data["quantity"] = round(data["quantity"] + quantity, 3)
                data["status"] = "HEALTHY"
                data["last_updated"] = now
                self._persist()
                return

        pid = f"prod_added_{len(self.pantry) + 1}"
        new_qty = float(quantity) if quantity else 1.0
        self.pantry[pid] = {
            "name": name.title() if name else (category.title() if category else "Item"),
            "quantity": new_qty,
            "unit": unit or "units",
            "daily_consumption": max(0.05, round(new_qty / 14, 3)),
            "status": "HEALTHY",
            "category": category.title() if category else "General",
            "preferred": False,
            "last_updated": now,
        }
        self._persist()

    def update_item(
        self,
        item_name_or_id: str,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update existing item or add new pantry item."""
        now = _now_iso()
        target_item = None
        target_pid = None
        key_lower = item_name_or_id.lower().strip()

        if item_name_or_id in self.pantry:
            target_pid = item_name_or_id
            target_item = self.pantry[item_name_or_id]
        else:
            for pid, data in self.pantry.items():
                if (
                    key_lower in data["name"].lower()
                    or key_lower in data["category"].lower()
                    or data["name"].lower() in key_lower
                ):
                    target_pid = pid
                    target_item = data
                    break

        if target_item:
            if quantity is not None:
                target_item["quantity"] = round(float(quantity), 3)
            if unit:
                target_item["unit"] = unit
            if status:
                target_item["status"] = status
            target_item["last_updated"] = now
            self._persist()
            return {"product_id": target_pid, **target_item}
        else:
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
                "preferred": False,
                "last_updated": now,
            }
            self._persist()
            return {"product_id": new_pid, **self.pantry[new_pid]}

    def report_depleted(self, item_name: str) -> Dict[str, Any]:
        """Mark an item in the pantry as depleted/empty."""
        return self.update_item(item_name, quantity=0.0, status="LOW")
