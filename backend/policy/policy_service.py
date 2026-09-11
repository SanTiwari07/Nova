from typing import List

class PolicyService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.automatic_categories = ["Milk", "Rice", "Atta", "Eggs", "Bread"]
        self.ask_categories = ["Snacks", "Electronics"]
        self.restricted_categories = ["Alcohol", "Tobacco"]
        
    def update_rules(self, automatic: List[str], ask: List[str], restricted: List[str]):
        self.automatic_categories = automatic
        self.ask_categories = ask
        self.restricted_categories = restricted
        
    async def is_category_allowed(self, category: str) -> bool:
        # Check against restricted
        cat = category.lower() if category else ""
        for r in self.restricted_categories:
            if r.lower() in cat:
                return False
        return True
        
    async def requires_ask(self, category: str) -> bool:
        cat = category.lower() if category else ""
        for a in self.ask_categories:
            if a.lower() in cat:
                return True
        return False
        
    async def is_automatic(self, category: str) -> bool:
        cat = category.lower() if category else ""
        for a in self.automatic_categories:
            if a.lower() in cat:
                return True
        return False
