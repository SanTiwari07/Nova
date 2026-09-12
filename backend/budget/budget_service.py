class BudgetService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.monthly_budget = 5500
        self.spent = 3940
        self.auto_limit = 500
        
    def set_budget(self, amount: float):
        self.monthly_budget = amount
        
    def set_auto_limit(self, amount: float):
        self.auto_limit = amount
        
    async def get_remaining_budget(self) -> float:
        return self.monthly_budget - self.spent
        
    async def get_auto_buy_limit(self) -> float:
        return self.auto_limit
        
    async def record_spend(self, amount: float):
        self.spent += amount

    def get_status(self) -> dict:
        return {
            "monthly": self.monthly_budget,
            "spent": self.spent,
            "remaining": self.monthly_budget - self.spent,
            "auto_limit": self.auto_limit
        }
