from typing import Dict, Any, List


class SavingsEngine:
    """
    Evaluates current household shopping plan for savings opportunities.
    Considers: price timing, pack size optimization, brand alternatives, retailer comparison.
    """

    def get_savings_opportunities(self, nova_cart_items: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Seeded savings opportunities for demo
        opportunities = [
            {
                "id": "sav_001",
                "type": "PRICE_WAIT",
                "product_id": "prod_000090",
                "product_name": "Surf Excel Detergent 3kg",
                "current_price": 435,
                "target_price": 380,
                "potential_saving": 55,
                "action": "WAIT",
                "reason": "Price is 14% above your average. Detergent prices typically drop by month-end.",
                "confidence": 0.72,
            },
            {
                "id": "sav_002",
                "type": "PACK_SIZE",
                "product_id": "prod_000050",
                "product_name": "Tata Salt 1kg",
                "current_price": 50,
                "target_price": 38,
                "potential_saving": 12,
                "action": "CHANGE_QUANTITY",
                "reason": "Buying 2kg pack is cheaper per kg than buying two 1kg packs.",
                "confidence": 0.91,
            },
            {
                "id": "sav_003",
                "type": "RETAILER",
                "product_id": "prod_000030",
                "product_name": "Fortune Sunflower Oil 5L",
                "current_price": 762,
                "target_price": 698,
                "potential_saving": 64,
                "action": "SWITCH_RETAILER",
                "reason": "Zepto currently has this 8% cheaper. NOVA recommends staying on Amazon for Prime delivery.",
                "confidence": 0.65,
                "alternative_retailer": "Zepto",
                "alternative_price": 698,
            },
        ]

        total_saving = sum(o["potential_saving"] for o in opportunities)

        return {
            "opportunities": opportunities,
            "total_potential_saving": total_saving,
            "opportunity_count": len(opportunities),
            "summary": f"NOVA found {len(opportunities)} ways to save ₹{total_saving} on your household shopping.",
            "source": "AMAZON_MOCK",
        }
