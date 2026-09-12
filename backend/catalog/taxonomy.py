"""
NOVA Canonical Product Taxonomy & Classification Layer.
Provides deterministic, semantic classification of products into categories,
subcategories, and homepage merchandising sections.
Strictly prevents cross-category contamination (e.g., Milk in Cleaning, Tea in Snacks).
"""

import re
from typing import Dict, Any, List, Optional, Tuple

CANONICAL_CATEGORIES: Dict[str, Dict[str, Any]] = {
    "Milk & Dairy": {
        "slug": "milk-and-dairy",
        "subcategories": ["Milk", "Curd & Dahi", "Paneer", "Butter", "Cheese", "Ghee", "Dairy Beverages"],
        "section": "dairy",
        "keywords": ["milk", "curd", "dahi", "paneer", "butter", "cheese", "ghee", "yogurt", "cream", "taaza", "nandini", "dairy", "chaas", "lassi", "cow milk", "buffalo milk"],
    },
    "Atta & Rice": {
        "slug": "atta-and-rice",
        "subcategories": ["Atta & Flour", "Basmati Rice", "Raw Rice", "Poha", "Suji & Rava", "Grains"],
        "section": "groceries",
        "keywords": ["atta", "rice", "basmati", "flour", "wheat", "maida", "sooji", "suji", "rava", "besan", "poha", "kolam", "sona masoori", "grain"],
    },
    "Cooking Oils": {
        "slug": "cooking-oils",
        "subcategories": ["Sunflower Oil", "Mustard Oil", "Groundnut Oil", "Rice Bran Oil", "Soyabean Oil", "Olive Oil"],
        "section": "groceries",
        "keywords": ["oil", "sunflower", "mustard", "groundnut", "refined", "soyabean", "tel", "kachi ghani", "edible oil"],
    },
    "Dal & Pulses": {
        "slug": "dal-and-pulses",
        "subcategories": ["Toor Dal", "Moong Dal", "Chana Dal", "Urad Dal", "Rajma", "Pulses & Lentils"],
        "section": "groceries",
        "keywords": ["dal", "pulses", "chana", "toor", "arhar", "moong", "urad", "rajma", "masoor", "lentil", "kabuli", "kala chana"],
    },
    "Instant Noodles": {
        "slug": "instant-noodles",
        "subcategories": ["Instant Noodles", "Cup Noodles", "Pasta & Macaroni", "Ramen"],
        "section": "snacks",
        "keywords": ["noodle", "noodles", "maggi", "pasta", "ramen", "macaroni", "yippee", "chow"],
    },
    "Tea & Staples": {
        "slug": "tea-and-staples",
        "subcategories": ["Tea", "Coffee", "Sugar", "Salt", "Spices"],
        "section": "groceries",
        "keywords": ["tea", "chai", "coffee", "taj mahal", "red label", "tata tea", "nescafe", "bru", "assam tea", "wagh bakri", "society tea", "salt", "sugar", "spices", "masala"],
    },
    "Snacks & Biscuits": {
        "slug": "snacks-and-biscuits",
        "subcategories": ["Biscuits & Cookies", "Chips & Namkeen", "Chocolates & Sweets", "Snacks"],
        "section": "snacks",
        "keywords": ["biscuit", "biscuits", "cookie", "cookies", "chips", "namkeen", "snack", "snacks", "chocolate", "chocolates", "cadbury", "parle", "good day", "marie", "oreo", "bhujia", "kurkure", "lays", "bingo", "rusk"],
    },
    "Beverages": {
        "slug": "beverages",
        "subcategories": ["Cold Drinks & Soda", "Fruit Juices", "Energy Drinks", "Mineral Water"],
        "section": "snacks",
        "keywords": ["beverage", "drink", "juice", "pepsi", "coke", "coca-cola", "sprite", "thums up", "frooti", "maaza", "real juice", "paper boat", "sting", "cold drink", "soda"],
    },
    "Cleaning & Toiletries": {
        "slug": "cleaning-and-toiletries",
        "subcategories": ["Detergent & Laundry", "Dishwash", "Floor & Surface Cleaners", "Toilet Cleaners", "Air Fresheners"],
        "section": "household",
        "keywords": ["detergent", "surf excel", "ariel", "rin", "tide", "wheel", "cleaner", "harpic", "vim", "dishwash", "lizol", "toilet", "colin", "fabric conditioner", "comfort", "laundry"],
    },
    "Personal Care": {
        "slug": "personal-care",
        "subcategories": ["Toothpaste & Oral Care", "Soaps & Body Wash", "Shampoo & Hair Care", "Handwash"],
        "section": "household",
        "keywords": ["toothpaste", "colgate", "sensodyne", "close up", "soap", "dettol", "lifebuoy", "dove", "pears", "shampoo", "head & shoulders", "handwash"],
    },
}

# Alias for backward compatibility
CANONICAL_CATEGORIES["Tea & Coffee"] = CANONICAL_CATEGORIES["Tea & Staples"]

SECTION_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "deals": {
        "id": "deals",
        "title": "Deals of the Day | Grocery & Essentials",
        "description": "Curated limited-time discounts across everyday household essentials.",
        "allowed_categories": list(CANONICAL_CATEGORIES.keys()),
        "view_all_link": "/catalog",
    },
    "usuals": {
        "id": "usuals",
        "title": "Frequently Purchased by Your Household",
        "description": "Routine staples predicted and monitored by NOVA Autopilot.",
        "allowed_categories": ["Milk & Dairy", "Tea & Staples", "Tea & Coffee", "Atta & Rice", "Cooking Oils"],
        "view_all_link": "/catalog?category=Milk%20%26%20Dairy",
    },
    "groceries": {
        "id": "groceries",
        "title": "Kitchen & Cooking Staples",
        "description": "Atta, premium basmati rice, dals, pulses, and pure cooking oils.",
        "allowed_categories": ["Atta & Rice", "Cooking Oils", "Dal & Pulses", "Tea & Staples"],
        "view_all_link": "/catalog?category=Atta%20%26%20Rice",
    },
    "household": {
        "id": "household",
        "title": "Household Cleaning & Laundry",
        "description": "Laundry detergents, dishwash, surface disinfectants, and personal hygiene.",
        "allowed_categories": ["Cleaning & Toiletries", "Personal Care"],
        "disallowed_categories": ["Milk & Dairy", "Tea & Staples", "Tea & Coffee", "Atta & Rice", "Cooking Oils", "Dal & Pulses", "Instant Noodles", "Snacks & Biscuits", "Beverages"],
        "view_all_link": "/catalog?category=Cleaning%20%26%20Toiletries",
    },
    "snacks": {
        "id": "snacks",
        "title": "Snacks, Biscuits & Beverages",
        "description": "Tea-time biscuits, instant noodles, savoury namkeen, and refreshing beverages.",
        "allowed_categories": ["Snacks & Biscuits", "Instant Noodles", "Beverages"],
        "disallowed_categories": ["Milk & Dairy", "Tea & Staples", "Tea & Coffee", "Atta & Rice", "Cooking Oils", "Dal & Pulses", "Cleaning & Toiletries", "Personal Care"],
        "view_all_link": "/catalog?category=Snacks%20%26%20Biscuits",
    },
}


def _match_keywords(text: str, keywords: List[str]) -> bool:
    """Safe keyword matching using word boundaries for all tokens to avoid false substrings (e.g. 'lassi' in 'classic', 'rin' in 'drink')."""
    for kw in keywords:
        kw_clean = kw.strip()
        if not kw_clean:
            continue
        pattern = r'\b' + re.escape(kw_clean) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def classify_product(
    name: str,
    brand: Optional[str] = None,
    raw_category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Deterministically classifies a product into canonical category, subcategory,
    section, and keywords.
    """
    clean_name = str(name or "").strip()
    clean_brand = str(brand or "").strip()
    clean_raw_cat = str(raw_category or "").strip().lower()
    search_text = f"{clean_brand} {clean_name} {clean_raw_cat}".lower()

    # 1. BEVERAGES (Check cold drinks and juices first so words like 'drink' aren't confused)
    if _match_keywords(search_text, [
        "pepsi", "coca-cola", "coke", "sprite", "thums up", "fanta", "mirinda", "limca",
        "frooti", "maaza", "real juice", "paper boat", "sting", "red bull", "cold drink",
        "soft drink", "fruit juice", "appy fizz", "slice", "seven up", "7up", "soda", "mineral water"
    ]):
        sub = "Fruit Juices" if _match_keywords(search_text, ["juice", "frooti", "maaza", "paper boat", "real"]) else \
              "Cold Drinks & Soda"
        return {
            "category": "Beverages",
            "subcategory": sub,
            "section": "snacks",
            "keywords": ["beverages", "cold_drinks", "drinks", "juice", "refreshment"],
        }

    # 2. CLEANING & TOILETRIES (Household cleaning, detergent, dishwash, garbage bags, towels)
    if _match_keywords(search_text, [
        "detergent", "surf excel", "ariel", "rin", "tide", "wheel", "washing powder",
        "liquid detergent", "fabric conditioner", "comfort", "harpic", "vim", "dishwash",
        "lizol", "floor cleaner", "toilet cleaner", "colin", "glass cleaner", "drain cleaner",
        "garbage bags", "kitchen towels", "toilet roll", "tissues", "cleaning", "scrubber", "sponge"
    ]):
        sub = "Detergent & Laundry" if _match_keywords(search_text, ["detergent", "surf", "ariel", "tide", "rin", "wheel", "laundry", "wash"]) else \
              "Dishwash" if _match_keywords(search_text, ["dishwash", "vim", "scrub"]) else \
              "Toilet Cleaners" if _match_keywords(search_text, ["harpic", "toilet"]) else \
              "Floor & Surface Cleaners"
        return {
            "category": "Cleaning & Toiletries",
            "subcategory": sub,
            "section": "household",
            "keywords": ["cleaning", "household", "laundry", "toiletries", "detergent", "cleaner"],
        }

    # 3. PERSONAL CARE (Soaps, body wash, shampoo, oral care)
    if _match_keywords(search_text, [
        "toothpaste", "colgate", "sensodyne", "close up", "darlie", "oral-b", "toothbrush",
        "shampoo", "head & shoulders", "dove", "pantene", "tresemme",
        "body wash", "lifebuoy", "dettol soap", "bathing soap", "soap", "soaps", "bathing bar", "pears", "cinthol", "lux", "handwash"
    ]) and not _match_keywords(search_text, ["dishwash", "floor"]):
        sub = "Toothpaste & Oral Care" if _match_keywords(search_text, ["toothpaste", "colgate", "sensodyne", "tooth"]) else \
              "Shampoo & Hair Care" if _match_keywords(search_text, ["shampoo"]) else \
              "Soaps & Body Wash"
        return {
            "category": "Personal Care",
            "subcategory": sub,
            "section": "household",
            "keywords": ["personal_care", "hygiene", "soap", "toothpaste", "toiletries"],
        }

    # 4. MILK & DAIRY
    if _match_keywords(search_text, [
        "milk", "curd", "dahi", "paneer", "butter", "cheese", "ghee", "yogurt",
        "cream", "taaza", "nandini", "dairy", "chaas", "lassi", "cow milk", "buffalo milk", "a2 milk"
    ]) and not _match_keywords(search_text, ["biscuit", "cookie", "chocolate", "shake", "detergent", "soap"]):
        sub = "Milk" if _match_keywords(search_text, ["milk", "taaza", "cow milk", "toned", "pasteurised"]) else \
              "Curd & Dahi" if _match_keywords(search_text, ["curd", "dahi", "yogurt"]) else \
              "Paneer" if "paneer" in search_text else \
              "Butter" if "butter" in search_text else \
              "Cheese" if "cheese" in search_text else \
              "Ghee" if "ghee" in search_text else "Dairy Products"
        return {
            "category": "Milk & Dairy",
            "subcategory": sub,
            "section": "dairy",
            "keywords": ["milk", "dairy", "usual", "staple", "breakfast"],
        }

    # 5. INSTANT NOODLES & PASTA
    if _match_keywords(search_text, [
        "noodle", "noodles", "maggi", "pasta", "ramen", "macaroni", "yippee", "chow mein", "pazzta", "wickedgud"
    ]):
        sub = "Cup Noodles" if "cup" in search_text else \
              "Pasta & Macaroni" if _match_keywords(search_text, ["pasta", "macaroni", "pazzta"]) else \
              "Instant Noodles"
        kw = ["noodles", "instant_noodles", "snacks", "instant_food"]
        if "maggi" in search_text:
            kw.append("maggi")
        return {
            "category": "Instant Noodles",
            "subcategory": sub,
            "section": "snacks",
            "keywords": kw,
        }

    # 6. TEA & COFFEE (Never classify as snacks)
    if _match_keywords(search_text, [
        "tea", "chai", "coffee", "tata tea", "red label", "taj mahal", "wagh bakri",
        "society tea", "nescafe", "bru", "assam tea", "ctc tea", "green tea",
        "chicory", "koffelo", "filter coffee", "espresso", "davidoff", "continental coffee"
    ]):
        sub = "Coffee" if _match_keywords(search_text, ["coffee", "nescafe", "bru", "chicory", "koffelo", "espresso", "davidoff", "continental"]) else "Tea"
        return {
            "category": "Tea & Staples",
            "subcategory": sub,
            "section": "groceries",
            "keywords": ["tea", "coffee", "chai", "staples", "usual", "breakfast"],
        }

    # 7. SNACKS & BISCUITS (Excludes tea & coffee)
    if _match_keywords(search_text, [
        "biscuit", "biscuits", "cookie", "cookies", "chips", "namkeen", "snack", "snacks",
        "chocolate", "chocolates", "cadbury", "parle", "good day", "marie gold", "oreo",
        "hide & seek", "bourbon", "monaco", "krackjack", "lays", "lay's", "kurkure",
        "bingo", "haldiram", "bhujia", "mixture", "sev", "rusk", "wafer", "dairy milk", "kitkat", "munch"
    ]) and not _match_keywords(search_text, ["tea", "chai", "coffee", "chicory", "koffelo"]):
        sub = "Biscuits & Cookies" if _match_keywords(search_text, ["biscuit", "cookie", "parle", "good day", "marie", "oreo", "bourbon", "rusk"]) else \
              "Chocolates & Sweets" if _match_keywords(search_text, ["chocolate", "cadbury", "dairy milk", "kitkat", "munch"]) else \
              "Chips & Namkeen"
        return {
            "category": "Snacks & Biscuits",
            "subcategory": sub,
            "section": "snacks",
            "keywords": ["snacks", "biscuits", "namkeen", "chips", "munchies"],
        }

    # 8. COOKING OILS
    if _match_keywords(search_text, [
        "sunflower oil", "mustard oil", "groundnut oil", "refined oil", "soyabean oil",
        "rice bran oil", "olive oil", "kachi ghani", "edible oil", "saffola", "gemini oil", "fortune oil", "cooking oil"
    ]) or (_match_keywords(search_text, ["oil", "tel"]) and not _match_keywords(search_text, ["hair", "shampoo", "massage", "baby"])):
        sub = "Sunflower Oil" if "sunflower" in search_text else \
              "Mustard Oil" if "mustard" in search_text else \
              "Groundnut Oil" if "groundnut" in search_text else \
              "Rice Bran Oil" if "rice bran" in search_text else \
              "Cooking Oils"
        return {
            "category": "Cooking Oils",
            "subcategory": sub,
            "section": "groceries",
            "keywords": ["oil", "cooking_oils", "staple", "groceries", "usual"],
        }

    # 9. DAL & PULSES
    if _match_keywords(search_text, [
        "dal", "pulses", "toor dal", "arhar dal", "moong dal", "chana dal", "urad dal",
        "masoor dal", "rajma", "chana", "kabuli chana", "kala chana", "lentil", "lentils"
    ]):
        sub = "Toor Dal" if _match_keywords(search_text, ["toor", "arhar"]) else \
              "Moong Dal" if "moong" in search_text else \
              "Chana Dal" if "chana" in search_text else \
              "Rajma" if "rajma" in search_text else \
              "Dal & Pulses"
        return {
            "category": "Dal & Pulses",
            "subcategory": sub,
            "section": "groceries",
            "keywords": ["dal", "pulses", "staple", "groceries", "grains"],
        }

    # 10. ATTA & RICE (GRAINS)
    if _match_keywords(search_text, [
        "atta", "rice", "basmati", "flour", "wheat", "maida", "sooji", "suji", "rava",
        "besan", "poha", "kolam", "sona masoori", "indrayani", "daawat", "india gate", "fortune chakki"
    ]):
        sub = "Basmati Rice" if "basmati" in search_text else \
              "Atta & Flour" if _match_keywords(search_text, ["atta", "flour", "wheat", "maida", "besan", "suji", "rava"]) else \
              "Raw Rice" if _match_keywords(search_text, ["rice", "kolam", "sona masoori", "indrayani"]) else \
              "Poha" if "poha" in search_text else \
              "Atta & Rice"
        return {
            "category": "Atta & Rice",
            "subcategory": sub,
            "section": "groceries",
            "keywords": ["atta", "rice", "grains", "flour", "staple", "groceries", "usual"],
        }

    # 11. SPICES, SALT & SUGAR (STAPLES)
    if _match_keywords(search_text, [
        "salt", "sugar", "spices", "masala", "turmeric", "haldi", "chilli", "mirch", "jeera", "cumin", "pepper"
    ]):
        return {
            "category": "Tea & Staples",
            "subcategory": "Salt, Sugar & Spices",
            "section": "groceries",
            "keywords": ["staples", "spices", "salt", "sugar", "groceries"],
        }

    # Map raw category strings to canonical categories
    RAW_CATEGORY_MAP = {
        "atta": ("Atta & Rice", "Atta & Flour", "groceries"),
        "rice": ("Atta & Rice", "Basmati Rice", "groceries"),
        "grains": ("Atta & Rice", "Grains", "groceries"),
        "flour": ("Atta & Rice", "Atta & Flour", "groceries"),
        "milk": ("Milk & Dairy", "Milk", "dairy"),
        "dairy": ("Milk & Dairy", "Dairy Products", "dairy"),
        "ghee": ("Milk & Dairy", "Ghee", "dairy"),
        "oil": ("Cooking Oils", "Cooking Oils", "groceries"),
        "cooking oils": ("Cooking Oils", "Cooking Oils", "groceries"),
        "dal": ("Dal & Pulses", "Dal & Pulses", "groceries"),
        "pulses": ("Dal & Pulses", "Dal & Pulses", "groceries"),
        "noodles": ("Instant Noodles", "Instant Noodles", "snacks"),
        "instant noodles": ("Instant Noodles", "Instant Noodles", "snacks"),
        "tea": ("Tea & Coffee", "Chai & Black Tea", "tea-coffee"),
        "coffee": ("Tea & Coffee", "Instant Coffee", "tea-coffee"),
        "tea & coffee": ("Tea & Coffee", "Chai & Black Tea", "tea-coffee"),
        "tea & staples": ("Tea & Staples", "Salt, Sugar & Spices", "groceries"),
        "staples": ("Tea & Staples", "Salt, Sugar & Spices", "groceries"),
        "salt": ("Tea & Staples", "Salt, Sugar & Spices", "groceries"),
        "sugar": ("Tea & Staples", "Salt, Sugar & Spices", "groceries"),
        "spices": ("Tea & Staples", "Salt, Sugar & Spices", "groceries"),
        "biscuits": ("Snacks & Biscuits", "Biscuits & Cookies", "snacks"),
        "snacks": ("Snacks & Biscuits", "Snacks", "snacks"),
        "beverages": ("Beverages", "Cold Drinks & Soda", "snacks"),
        "drinks": ("Beverages", "Cold Drinks & Soda", "snacks"),
        "cleaning": ("Cleaning & Toiletries", "Floor & Surface Cleaners", "household"),
        "detergent": ("Cleaning & Toiletries", "Detergent & Laundry", "household"),
        "dishwash": ("Cleaning & Toiletries", "Dishwash", "household"),
        "cleaning & toiletries": ("Cleaning & Toiletries", "Detergent & Laundry", "household"),
        "personal care": ("Personal Care", "Soaps & Body Wash", "household"),
        "soap": ("Personal Care", "Soaps & Body Wash", "household"),
        "shampoo": ("Personal Care", "Shampoo & Hair Care", "household"),
        "toothpaste": ("Personal Care", "Toothpaste & Oral Care", "household"),
    }
    for k, (c, sub, sec) in RAW_CATEGORY_MAP.items():
        if k == clean_raw_cat or k in clean_raw_cat:
            return {
                "category": c,
                "subcategory": sub,
                "section": sec,
                "keywords": [k],
            }

    return {
        "category": "Atta & Rice",
        "subcategory": "Grains & Staples",
        "section": "groceries",
        "keywords": ["staple"],
    }


def is_product_allowed_in_section(product: Dict[str, Any], section_id: str) -> bool:
    """
    Validates whether a product is semantically permissible in a section.
    Enforces zero cross-category contamination.
    """
    sec_cfg = SECTION_DEFINITIONS.get(section_id)
    if not sec_cfg:
        return True

    category = product.get("category", "")
    allowed = sec_cfg.get("allowed_categories", [])
    disallowed = sec_cfg.get("disallowed_categories", [])

    if disallowed and category in disallowed:
        return False

    return category in allowed
