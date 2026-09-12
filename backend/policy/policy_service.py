from typing import List

class PolicyService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.automatic_categories = ["Milk", "Rice", "Atta", "Eggs", "Bread"]
        self.ask_categories = ["Snacks", "Electronics"]
        self.restricted_categories = ["Alcohol", "Tobacco"]
        
    def get_rules(self) -> dict:
        return {
            "automatic_categories": list(self.automatic_categories),
            "ask_categories": list(self.ask_categories),
            "restricted_categories": list(self.restricted_categories),
        }

    def update_rules(self, automatic: List[str], ask: List[str], restricted: List[str]):
        self.automatic_categories = automatic
        self.ask_categories = ask
        self.restricted_categories = restricted

    def set_category_policy(self, category: str, policy_type: str) -> dict:
        """Set a single category to 'automatic', 'ask', or 'restricted'."""
        cat_clean = category.strip()
        # Remove from all first
        self.automatic_categories = [c for c in self.automatic_categories if c.lower() != cat_clean.lower()]
        self.ask_categories = [c for c in self.ask_categories if c.lower() != cat_clean.lower()]
        self.restricted_categories = [c for c in self.restricted_categories if c.lower() != cat_clean.lower()]

        pt = policy_type.lower()
        if "auto" in pt:
            self.automatic_categories.append(cat_clean.title())
        elif "ask" in pt:
            self.ask_categories.append(cat_clean.title())
        elif "restrict" in pt or "block" in pt:
            self.restricted_categories.append(cat_clean.title())
        return self.get_rules()
        
    async def is_category_allowed(self, category: str) -> bool:
        # Check against restricted
        cat = category.lower().strip() if category else ""
        for r in self.restricted_categories:
            rc = r.lower().strip()
            if rc and (rc in cat or cat in rc):
                return False
        return True
        
    async def requires_ask(self, category: str) -> bool:
        cat = category.lower().strip() if category else ""
        for a in self.ask_categories:
            ac = a.lower().strip()
            if ac and (ac in cat or cat in ac):
                return True
        return False
        
    async def is_automatic(self, category: str) -> bool:
        cat = category.lower().strip() if category else ""
        for a in self.automatic_categories:
            ac = a.lower().strip()
            if ac and (ac in cat or cat in ac):
                return True
        return False
