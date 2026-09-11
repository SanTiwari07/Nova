from typing import Dict, Any, List, Optional


class PriceService:
    """
    Price intelligence service for household products.
    Provides BUY/WAIT recommendations based on current vs historical prices.
    Source: AMAZON_MOCK
    """

    def __init__(self):
        self._price_watch = self._build_price_watch()

    def _build_price_watch(self) -> List[Dict[str, Any]]:
        return [
            {
                "product_id": "prod_000090",
                "asin": "B07DET001",
                "name": "Surf Excel Detergent 3kg",
                "brand": "Surf Excel",
                "pack_size": "3 kg",
                "category": "Detergent",
                "current_price": 435,
                "typical_price": 380,
                "lowest_observed": 349,
                "highest_observed": 449,
                "target_price": 380,
                "price_trend": "RISING",
                "price_vs_avg_pct": 14.5,
                "recommendation": "WAIT",
                "recommendation_reason": "Current Amazon price is 14% above your usual purchase price. You have ~15 days of supply remaining.",
                "days_remaining": 15,
                "watching": True,
                "source": "AMAZON_MOCK",
            },
            {
                "product_id": "prod_000010",
                "asin": "B08XYZABC1",
                "name": "India Gate Basmati Rice 5kg",
                "brand": "India Gate",
                "pack_size": "5 kg",
                "category": "Rice",
                "current_price": 469,
                "typical_price": 485,
                "lowest_observed": 440,
                "highest_observed": 510,
                "target_price": 460,
                "price_trend": "FALLING",
                "price_vs_avg_pct": -3.3,
                "recommendation": "BUY",
                "recommendation_reason": "Current Amazon price is 3% below your typical price. You are expected to need this in 7 days.",
                "days_remaining": 7,
                "watching": False,
                "source": "AMAZON_MOCK",
            },
            {
                "product_id": "prod_000030",
                "asin": "B07OIL0030",
                "name": "Fortune Sunflower Oil 5L",
                "brand": "Fortune",
                "pack_size": "5 L",
                "category": "Oil",
                "current_price": 762,
                "typical_price": 699,
                "lowest_observed": 649,
                "highest_observed": 789,
                "target_price": 699,
                "price_trend": "RISING",
                "price_vs_avg_pct": 9.0,
                "recommendation": "WAIT",
                "recommendation_reason": "You have ~46 days of supply. Current price is 9% above your average. No urgency to buy now.",
                "days_remaining": 46,
                "watching": True,
                "source": "AMAZON_MOCK",
            },
            {
                "product_id": "prod_000001",
                "asin": "B07TQHXVB5",
                "name": "Aashirvaad Whole Wheat Atta 5kg",
                "brand": "Aashirvaad",
                "pack_size": "5 kg",
                "category": "Atta",
                "current_price": 289,
                "typical_price": 298,
                "lowest_observed": 265,
                "highest_observed": 319,
                "target_price": 280,
                "price_trend": "STABLE",
                "price_vs_avg_pct": -3.0,
                "recommendation": "BUY",
                "recommendation_reason": "Price is slightly below your average. You are expected to need this in 6 days. Good time to buy.",
                "days_remaining": 6,
                "watching": False,
                "source": "AMAZON_MOCK",
            },
            {
                "product_id": "prod_000080",
                "asin": "B07TEA001",
                "name": "Tata Chai Classic Tea 500g",
                "brand": "Tata Tea",
                "pack_size": "500 g",
                "category": "Tea",
                "current_price": 209,
                "typical_price": 220,
                "lowest_observed": 199,
                "highest_observed": 235,
                "target_price": 210,
                "price_trend": "FALLING",
                "price_vs_avg_pct": -5.0,
                "recommendation": "BUY",
                "recommendation_reason": "Price is 5% below your typical purchase price. Expected need in 6 days.",
                "days_remaining": 6,
                "watching": False,
                "source": "AMAZON_MOCK",
            },
        ]

    def get_price_watch_items(self) -> List[Dict[str, Any]]:
        return self._price_watch

    def get_price_recommendation(self, product_id: str) -> Optional[Dict[str, Any]]:
        for item in self._price_watch:
            if item["product_id"] == product_id:
                return item
        return None

    def is_price_above_average(self, product_id: str, threshold_pct: float = 8.0) -> bool:
        item = self.get_price_recommendation(product_id)
        if not item:
            return False
        return item["price_vs_avg_pct"] > threshold_pct
