"""
NOVA Intent Reconciliation Service
Deconstructs household meal/activity intents into concrete requirements,
reconciles them against live pantry stock, and identifies only the minimum
necessary items that need to be acquired.
"""

from typing import Dict, Any, List, Optional, Tuple
import re


MEAL_RECIPES: Dict[str, Dict[str, Any]] = {
    "maggi": {
        "name": "Maggi Instant Noodles",
        "keywords": ["maggi", "noodle", "noodles", "ramen"],
        "components": [
            {
                "item": "Maggi Noodles",
                "category": "Instant Noodles",
                "keywords": ["maggi", "noodle"],
                "search_query": "maggi noodles",
                "essential": True,
                "needed_qty": 1.0,
                "unit": "pack"
            },
            {
                "item": "Cooking Oil",
                "category": "Cooking Oils",
                "keywords": ["oil", "sunflower", "mustard", "olive"],
                "search_query": "cooking oil",
                "essential": False,
                "needed_qty": 0.05,
                "unit": "L"
            },
            {
                "item": "Salt & Spices",
                "category": "Spices & Seasonings",
                "keywords": ["salt", "spice", "masala"],
                "search_query": "salt",
                "essential": False,
                "needed_qty": 0.02,
                "unit": "kg"
            }
        ]
    },
    "chai": {
        "name": "Indian Milk Tea / Chai",
        "keywords": ["chai", "tea"],
        "components": [
            {
                "item": "Tea Leaves",
                "category": "Tea & Coffee",
                "keywords": ["tea"],
                "search_query": "tea",
                "essential": True,
                "needed_qty": 0.05,
                "unit": "kg"
            },
            {
                "item": "Fresh Milk",
                "category": "Milk & Dairy",
                "keywords": ["milk"],
                "search_query": "milk",
                "essential": True,
                "needed_qty": 0.25,
                "unit": "L"
            },
            {
                "item": "Sugar",
                "category": "Sugar & Sweeteners",
                "keywords": ["sugar"],
                "search_query": "sugar",
                "essential": False,
                "needed_qty": 0.05,
                "unit": "kg"
            }
        ]
    },
    "dal_rice": {
        "name": "Dal & Rice",
        "keywords": ["dal", "rice", "khichdi"],
        "components": [
            {
                "item": "Rice",
                "category": "Atta & Rice",
                "keywords": ["rice"],
                "search_query": "rice",
                "essential": True,
                "needed_qty": 0.5,
                "unit": "kg"
            },
            {
                "item": "Toor / Moong Dal",
                "category": "Dals & Pulses",
                "keywords": ["dal", "pulse"],
                "search_query": "toor dal",
                "essential": True,
                "needed_qty": 0.25,
                "unit": "kg"
            },
            {
                "item": "Cooking Oil / Ghee",
                "category": "Cooking Oils",
                "keywords": ["oil", "ghee"],
                "search_query": "cooking oil",
                "essential": False,
                "needed_qty": 0.05,
                "unit": "L"
            }
        ]
    },
    "poha": {
        "name": "Poha (Flattened Rice Breakfast)",
        "keywords": ["poha", "flattened rice", "aval"],
        "components": [
            {
                "item": "Poha / Flattened Rice",
                "category": "Atta & Rice",
                "keywords": ["poha", "flattened rice", "aval"],
                "search_query": "poha",
                "essential": True,
                "needed_qty": 0.5,
                "unit": "kg"
            },
            {
                "item": "Cooking Oil",
                "category": "Cooking Oils",
                "keywords": ["oil", "sunflower", "mustard", "olive"],
                "search_query": "cooking oil",
                "essential": False,
                "needed_qty": 0.05,
                "unit": "L"
            },
            {
                "item": "Salt & Spices",
                "category": "Spices & Seasonings",
                "keywords": ["salt", "spice", "turmeric", "mustard seed"],
                "search_query": "salt",
                "essential": False,
                "needed_qty": 0.02,
                "unit": "kg"
            }
        ]
    },
    "pasta": {
        "name": "Italian Pasta",
        "keywords": ["pasta", "macaroni", "penne", "spaghetti"],
        "components": [
            {
                "item": "Pasta / Penne",
                "category": "Instant Noodles",
                "keywords": ["pasta", "penne", "macaroni"],
                "search_query": "pasta",
                "essential": True,
                "needed_qty": 0.5,
                "unit": "kg"
            },
            {
                "item": "Cooking Oil / Olive Oil",
                "category": "Cooking Oils",
                "keywords": ["oil", "olive oil"],
                "search_query": "cooking oil",
                "essential": False,
                "needed_qty": 0.05,
                "unit": "L"
            },
            {
                "item": "Salt & Seasoning",
                "category": "Spices & Seasonings",
                "keywords": ["salt", "herb", "seasoning"],
                "search_query": "salt",
                "essential": False,
                "needed_qty": 0.02,
                "unit": "kg"
            }
        ]
    },
    "coffee": {
        "name": "Fresh Coffee",
        "keywords": ["coffee", "nescafe", "cappuccino", "espresso"],
        "components": [
            {
                "item": "Coffee Powder",
                "category": "Tea & Coffee",
                "keywords": ["coffee", "nescafe"],
                "search_query": "coffee",
                "essential": True,
                "needed_qty": 0.1,
                "unit": "kg"
            },
            {
                "item": "Fresh Milk",
                "category": "Milk & Dairy",
                "keywords": ["milk"],
                "search_query": "milk",
                "essential": True,
                "needed_qty": 0.25,
                "unit": "L"
            },
            {
                "item": "Sugar",
                "category": "Sugar & Sweeteners",
                "keywords": ["sugar"],
                "search_query": "sugar",
                "essential": False,
                "needed_qty": 0.05,
                "unit": "kg"
            }
        ]
    },
    "sandwich": {
        "name": "Sandwich",
        "keywords": ["sandwich", "toast"],
        "components": [
            {
                "item": "Bread",
                "category": "Bread & Bakery",
                "keywords": ["bread"],
                "search_query": "bread",
                "essential": True,
                "needed_qty": 1.0,
                "unit": "loaf"
            },
            {
                "item": "Butter / Cheese",
                "category": "Milk & Dairy",
                "keywords": ["butter", "cheese"],
                "search_query": "butter",
                "essential": True,
                "needed_qty": 0.1,
                "unit": "pack"
            }
        ]
    },
    "biryani": {
        "name": "Chicken or Vegetable Biryani",
        "keywords": ["biryani", "pulao", "biriyani", "dum biryani"],
        "components": [
            {
                "item": "Basmati Rice",
                "category": "Atta & Rice",
                "keywords": ["rice", "basmati", "kolam"],
                "search_query": "india gate basmati rice",
                "essential": True,
                "needed_qty": 1.0,
                "unit": "kg",
            },
            {
                "item": "Biryani Masala & Spices",
                "category": "Tea & Staples",
                "keywords": ["biryani masala", "garam masala", "spices", "masala"],
                "search_query": "biryani masala",
                "essential": True,
                "needed_qty": 1.0,
                "unit": "pack",
            },
            {
                "item": "Cooking Oil or Ghee",
                "category": "Cooking Oils",
                "keywords": ["oil", "ghee", "sunflower oil"],
                "search_query": "cooking oil",
                "essential": False,
                "needed_qty": 0.1,
                "unit": "L",
            },
            {
                "item": "Curd or Dahi",
                "category": "Milk & Dairy",
                "keywords": ["curd", "dahi", "yogurt"],
                "search_query": "amul dahi",
                "essential": False,
                "needed_qty": 0.4,
                "unit": "kg",
            },
        ],
    }
}


class IntentReconciliationService:
    """
    Decomposes meal/household intent into requirements, inspects current pantry
    inventory, and produces a reconciled shopping plan containing only missing items.
    """

    def __init__(self, inventory_service=None):
        self.inventory_service = inventory_service

    def _extract_serving_scale(self, text: str) -> Tuple[float, str]:
        """Extracts serving multiplier and returns (scale, cleaned_text)."""
        cleaned = text.lower().strip()
        serving_scale = 1.0
        
        # Check digit based: "for 6 people", "for 4 guests"
        scale_match = re.search(r"\bfor\s+(\d+)\s*(?:people|persons|guests|servings|members)?\b", cleaned)
        if scale_match:
            try:
                servings = int(scale_match.group(1))
                serving_scale = max(1.0, servings / 2.0)
                cleaned = re.sub(r"\bfor\s+\d+\s*(?:people|persons|guests|servings|members)?\b", "", cleaned).strip()
            except ValueError:
                pass
        else:
            word_nums = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
            for w, n in word_nums.items():
                pattern = rf"\bfor\s+{w}\s*(?:people|persons|guests|servings|members)?\b"
                if re.search(pattern, cleaned):
                    serving_scale = max(1.0, n / 2.0)
                    cleaned = re.sub(pattern, "", cleaned).strip()
                    break

        return serving_scale, cleaned

    def _match_recipe(self, intent_text: str) -> Optional[Dict[str, Any]]:
        cleaned = intent_text.lower()
        for recipe_key, recipe in MEAL_RECIPES.items():
            for kw in recipe["keywords"]:
                if re.search(r"\b" + re.escape(kw) + r"\b", cleaned):
                    return recipe
        return None

    def _extract_dynamic_dish(self, intent_text: str) -> Optional[str]:
        """Extracts dish name from phrases like 'I am making pasta tonight' or 'cook khichdi'."""
        _, cleaned = self._extract_serving_scale(intent_text)
        
        # Strip common trailing noise words
        noise_pattern = r"(?:\bwhat\b|\bhow\b|\bcan\b|\bi\b|\bneed\b|\bto\b|\bhave\b|\bplease\b|\.|\?|,).*$"
        cleaned_no_noise = re.sub(noise_pattern, "", cleaned).strip()
        
        patterns = [
            r"(?:make|making|cook|cooking|prepare|preparing|having|eat|eating|for)\s+([a-zA-Z\s]+?)(?:\s+tonight|\s+today|\s+for dinner|\s+for lunch|\s+for breakfast|$)",
            r"want\s+to\s+(?:make|cook|eat)\s+([a-zA-Z\s]+?)(?:\s+tonight|\s+today|$)",
            r"need\s+ingredients\s+for\s+([a-zA-Z\s]+?)(?:$)"
        ]
        for pat in patterns:
            m = re.search(pat, cleaned_no_noise)
            if m:
                dish = m.group(1).strip()
                if dish and len(dish.split()) <= 5:
                    return dish.title()
        return None

    async def reconcile_intent(self, intent_text: str) -> Dict[str, Any]:
        serving_scale, _ = self._extract_serving_scale(intent_text)
        recipe = self._match_recipe(intent_text)
        
        # If no predefined recipe matched, attempt dynamic recipe decomposition
        if not recipe:
            dish_name = self._extract_dynamic_dish(intent_text) or intent_text.strip()
            # Construct a dynamic recipe that checks staples (cooking oil, salt) in pantry
            recipe = {
                "name": dish_name if dish_name != intent_text.strip() else f"Household Request: {dish_name}",
                "keywords": [dish_name.lower()],
                "components": [
                    {
                        "item": dish_name,
                        "category": "General",
                        "keywords": [dish_name.lower()],
                        "search_query": dish_name.lower(),
                        "essential": True,
                        "needed_qty": 1.0,
                        "unit": "pack"
                    },
                    {
                        "item": "Cooking Oil",
                        "category": "Cooking Oils",
                        "keywords": ["oil", "sunflower", "mustard"],
                        "search_query": "cooking oil",
                        "essential": False,
                        "needed_qty": 0.05,
                        "unit": "L"
                    },
                    {
                        "item": "Salt & Spices",
                        "category": "Spices & Seasonings",
                        "keywords": ["salt", "spice"],
                        "search_query": "salt",
                        "essential": False,
                        "needed_qty": 0.02,
                        "unit": "kg"
                    }
                ]
            }

        pantry_items = self.inventory_service.get_all() if self.inventory_service else []

        available_in_pantry = []
        missing_items = []

        for comp in recipe["components"]:
            matched_pantry_item = None
            
            # Check pantry by category and keyword match
            comp_keywords = comp.get("keywords", [])
            comp_cat = comp.get("category", "").lower()
            for p in pantry_items:
                p_cat = p.get("category", "").lower()
                p_name = p.get("name", "").lower()
                
                if comp_keywords:
                    is_match = any(kw in p_name or kw in p_cat for kw in comp_keywords)
                else:
                    is_match = comp_cat and (comp_cat in p_cat or p_cat in comp_cat)
                
                if is_match:
                    matched_pantry_item = p
                    break

            if matched_pantry_item:
                qty = matched_pantry_item.get("quantity", 0)
                days_rem = matched_pantry_item.get("days_remaining", 0)
                status = matched_pantry_item.get("status", "HEALTHY")
                
                needed = comp.get("needed_qty", 0.05) * (serving_scale if serving_scale > 0 else 1.0)
                if status == "HEALTHY" and days_rem > 2 and qty >= needed:
                    available_in_pantry.append({
                        "item": comp["item"],
                        "matched_product": matched_pantry_item.get("name"),
                        "quantity": qty,
                        "unit": matched_pantry_item.get("unit"),
                        "days_remaining": days_rem,
                        "status": "HEALTHY",
                        "summary": f"{matched_pantry_item.get('name')} ({qty} {matched_pantry_item.get('unit')} in stock, ~{days_rem} days remaining)"
                    })
                    continue
                elif status == "LOW" or days_rem <= 2:
                    missing_items.append({
                        "item": comp["item"],
                        "search_query": comp["search_query"],
                        "category": comp["category"],
                        "reason": f"Stock is depleted or low in pantry ({qty} {matched_pantry_item.get('unit')} remaining)",
                        "priority": "HIGH"
                    })
                    continue

            # Not found in pantry at all
            missing_items.append({
                "item": comp["item"],
                "search_query": comp["search_query"],
                "category": comp["category"],
                "reason": "Missing from household pantry",
                "priority": "HIGH" if comp["essential"] else "LOW"
            })

        avail_names = [a["item"] for a in available_in_pantry]
        miss_names = [m["item"] for m in missing_items if m["priority"] == "HIGH"] or [m["item"] for m in missing_items]

        if avail_names and miss_names:
            summary = (
                f"Reconciliation for '{recipe['name']}': Household already has {', '.join(avail_names)} in healthy supply. "
                f"Only {', '.join(miss_names)} is missing from pantry and requires purchase."
            )
        elif miss_names:
            summary = f"Reconciliation for '{recipe['name']}': Missing {', '.join(miss_names)}."
        else:
            summary = f"Reconciliation for '{recipe['name']}': All ingredients are already available in healthy stock in your pantry!"

        return {
            "intent": intent_text,
            "activity_detected": True,
            "matched_activity": recipe["name"],
            "requirements": [c["item"] for c in recipe["components"]],
            "available_in_pantry": available_in_pantry,
            "missing_items": missing_items,
            "suggested_queries": [m["search_query"] for m in missing_items if m.get("priority") == "HIGH"] or [m["search_query"] for m in missing_items],
            "reconciliation_summary": summary
        }
