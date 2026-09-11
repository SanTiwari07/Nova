import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class ReminderEngine:
    """
    Manages contextual household reminders.
    Reminders are event-driven and tied to household state.
    """

    def __init__(self):
        self._reminders = self._seed_reminders()

    def _seed_reminders(self) -> List[Dict[str, Any]]:
        today = datetime.now()
        return [
            {
                "id": "rem_001",
                "type": "INVENTORY",
                "priority": "HIGH",
                "title": "Milk running low",
                "message": "Your milk is likely to run out in ~1 day. NOVA has added it to your household cart.",
                "product_id": "prod_000109",
                "product_name": "Amul Taaza Milk",
                "created_at": today.isoformat(),
                "due_at": (today + timedelta(days=1)).isoformat(),
                "status": "ACTIVE",
                "action_url": "/nova-cart",
            },
            {
                "id": "rem_002",
                "type": "MONTHLY_GROCERY",
                "priority": "MEDIUM",
                "title": "Monthly household cart ready",
                "message": "Your September household cart is ready. ₹4,872 of ₹5,500 budget. 17 items automatic, 1 needs approval.",
                "product_id": None,
                "product_name": None,
                "created_at": today.isoformat(),
                "due_at": today.isoformat(),
                "status": "ACTIVE",
                "action_url": "/autopilot",
            },
            {
                "id": "rem_003",
                "type": "PRICE_ALERT",
                "priority": "LOW",
                "title": "Detergent price is high",
                "message": "Surf Excel Detergent is ₹435 today, ₹55 above your usual price. NOVA recommends waiting.",
                "product_id": "prod_000090",
                "product_name": "Surf Excel Detergent",
                "created_at": today.isoformat(),
                "due_at": (today + timedelta(days=15)).isoformat(),
                "status": "ACTIVE",
                "action_url": "/price-watch",
            },
            {
                "id": "rem_004",
                "type": "REORDER",
                "priority": "MEDIUM",
                "title": "Atta likely needed soon",
                "message": "You usually buy Aashirvaad Atta every 28 days. Your last purchase was 22 days ago. Expected in ~6 days.",
                "product_id": "prod_000001",
                "product_name": "Aashirvaad Atta",
                "created_at": today.isoformat(),
                "due_at": (today + timedelta(days=6)).isoformat(),
                "status": "ACTIVE",
                "action_url": "/nova-cart",
            },
            {
                "id": "rem_005",
                "type": "APPROVAL",
                "priority": "HIGH",
                "title": "India Gate Rice needs your okay",
                "message": "Rice refill — ₹469. Within your budget but NOVA wants to confirm: do you want the 5kg pack this time?",
                "product_id": "prod_000010",
                "product_name": "India Gate Basmati Rice",
                "created_at": today.isoformat(),
                "due_at": (today + timedelta(days=7)).isoformat(),
                "status": "ACTIVE",
                "action_url": "/nova-cart",
            },
        ]

    def get_reminders(self, status: Optional[str] = "ACTIVE") -> List[Dict[str, Any]]:
        if status:
            return [r for r in self._reminders if r["status"] == status]
        return self._reminders

    def get_reminder(self, reminder_id: str) -> Optional[Dict[str, Any]]:
        for r in self._reminders:
            if r["id"] == reminder_id:
                return r
        return None

    def snooze(self, reminder_id: str, hours: int = 24) -> Optional[Dict[str, Any]]:
        r = self.get_reminder(reminder_id)
        if r:
            r["status"] = "SNOOZED"
            r["snoozed_until"] = (datetime.now() + timedelta(hours=hours)).isoformat()
        return r

    def complete(self, reminder_id: str) -> Optional[Dict[str, Any]]:
        r = self.get_reminder(reminder_id)
        if r:
            r["status"] = "COMPLETED"
            r["completed_at"] = datetime.now().isoformat()
        return r

    def dismiss(self, reminder_id: str) -> Optional[Dict[str, Any]]:
        r = self.get_reminder(reminder_id)
        if r:
            r["status"] = "DISMISSED"
        return r

    def create_reminder(self, type: str, title: str, message: str, product_id: str = None,
                        priority: str = "MEDIUM", hours_until_due: int = 24) -> Dict[str, Any]:
        reminder = {
            "id": f"rem_{uuid.uuid4().hex[:6]}",
            "type": type,
            "priority": priority,
            "title": title,
            "message": message,
            "product_id": product_id,
            "product_name": None,
            "created_at": datetime.now().isoformat(),
            "due_at": (datetime.now() + timedelta(hours=hours_until_due)).isoformat(),
            "status": "ACTIVE",
            "action_url": "/reminders",
        }
        self._reminders.append(reminder)
        return reminder

    def reset(self):
        self._reminders = self._seed_reminders()
