"""
Canonical Product Image Registry
=================================
Centralized, deterministic mapping from product-family slug → image URL.

Resolution rules
----------------
1. Strip size/weight tokens (kg, g, ml, L, pcs, pack of N) from the name.
2. Normalize to a slug (lowercase, spaces→hyphens, drop punctuation).
3. Exact registry match → return URL.
4. Weighted word-overlap match requiring ≥ 3 meaningful words AND
   at least one distinguishing keyword beyond just the brand.
5. Return None if no confident match (NEVER brand-only fallback).

A product that resolves to None will show a clean category placeholder in the
frontend. A wrong image is always worse than a professional placeholder.
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# Size/quantity token patterns to strip before slug generation
# ---------------------------------------------------------------------------
_SIZE_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*"
    r"(?:kg|g|gm|gram|grams|mg|ml|l|liter|litre|liters|litres|"
    r"pcs|pc|pieces|piece|pack|packet|count|rolls|roll|tabs|tab|"
    r"pouch|pouches|bottle|bottles|can|cans|cup|cups|bar|bars)\b",
    re.IGNORECASE,
)
_PACK_OF_PATTERN = re.compile(r"\bpack\s+of\s+\d+\b", re.IGNORECASE)
_PARENTHETICAL = re.compile(r"\(.*?\)")
_NON_ALNUM = re.compile(r"[^a-z0-9\s-]")
_MULTI_SPACE = re.compile(r"\s+")


def to_slug(name: str) -> str:
    """Convert a product name to a canonical slug (size-independent)."""
    if not name:
        return ""
    s = name.lower()
    s = _PARENTHETICAL.sub(" ", s)
    s = _PACK_OF_PATTERN.sub(" ", s)
    s = _SIZE_PATTERN.sub(" ", s)
    s = _NON_ALNUM.sub(" ", s)
    s = _MULTI_SPACE.sub(" ", s).strip()
    s = s.replace(" ", "-")
    # collapse multiple hyphens
    s = re.sub(r"-+", "-", s).strip("-")
    return s


# ---------------------------------------------------------------------------
# Stop-words that must NOT count towards a confident product match
# ---------------------------------------------------------------------------
_STOP_WORDS = {
    "the", "a", "an", "of", "and", "with", "for", "in", "by",
    "fresh", "original", "classic", "premium", "lite", "light",
    "pure", "natural", "rich", "super", "ultra", "new", "pack",
    "ml", "kg", "gm", "liter", "litre", "pcs", "count",
    "pouch", "bottle", "can", "roll", "bar", "cup",
}

# Brand-level stop-words — matching only on these is never enough
_BRAND_WORDS = {
    "amul", "tata", "nestle", "colgate", "dove", "dettol",
    "surf", "excel", "ariel", "vim", "lizol", "harpic",
    "fortune", "saffola", "aashirvaad", "pillsbury", "daawat",
    "kohinoor", "india", "gate", "maggi", "parle", "britannia",
    "lays", "kurkure", "haldirams", "cadbury", "oreo",
    "sunsilk", "head", "shoulders", "sensodyne", "everest", "mdh",
    "bru", "nescafe", "brooke", "bond", "real", "frooti", "paper",
    "boat", "pepsi", "sprite", "coca", "cola", "bingo", "dhara",
    "madhur", "yippee", "sunfeast", "nissin",
}


# ---------------------------------------------------------------------------
# The canonical registry
# Key = slug of the product FAMILY (no size).
# Value = verified image URL, or None (frontend shows category placeholder).
# ---------------------------------------------------------------------------
PRODUCT_IMAGE_REGISTRY: dict[str, Optional[str]] = {

    # ── ATTA ──────────────────────────────────────────────────────────────
    "aashirvaad-superior-mp-atta": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/CIW/2026/3/9/"
        "805a02b1-e08b-4d4b-aa8f-ab05cabb1e37_1780_1.png"
    ),
    "pillsbury-chakki-fresh-atta": None,
    "fortune-chakki-fresh-atta": None,

    # ── RICE ──────────────────────────────────────────────────────────────
    "india-gate-basmati-rice": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/CIW/2026/7/21/"
        "ed973afb-e397-4df3-8a23-6153474d93b0_450_1.png"
    ),
    # Sona Masoori is a DIFFERENT rice — must NOT share Basmati image
    "india-gate-sona-masoori-rice": None,
    "daawat-rozana-basmati-rice": None,
    "kohinoor-super-basmati-rice": None,

    # ── COOKING OIL ───────────────────────────────────────────────────────
    "fortune-sunflower-oil": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/ciw/2026/2/18/"
        "d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png"
    ),
    # Saffola Gold is a DIFFERENT oil brand/product — must NOT share Fortune image
    "saffola-gold-pro-healthy-lifestyle-oil": None,
    "dhara-kachi-ghani-mustard-oil": None,

    # ── SALT ──────────────────────────────────────────────────────────────
    "tata-salt-vacuum-evaporated": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/ciw/2025/12/18/"
        "219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png"
    ),
    # Tata Salt Lite is a different product (low-sodium) — must NOT share above image
    "tata-salt-lite-low-sodium": None,

    # ── SUGAR ─────────────────────────────────────────────────────────────
    "madhur-pure-hygienic-sugar": None,

    # ── GHEE / DAIRY ──────────────────────────────────────────────────────
    "amul-pure-cow-ghee": None,
    "amul-taaza-homogenised-toned-milk": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/ciw/2025/12/17/"
        "b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png"
    ),
    # Amul Gold is different from Amul Taaza — must NOT share the same image
    "amul-gold-full-cream-fresh-milk": None,
    "amul-pasteurised-butter": None,
    "amul-processed-cheese-blocks": None,

    # ── DAL ───────────────────────────────────────────────────────────────
    "tata-sampann-toor-dal": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/ciw/2025/12/16/"
        "eda40bda-ba3b-4fab-97ba-ccbd28c106cf_K71D7X8L8P_MN_15122025.png"
    ),
    "tata-sampann-moong-dal": None,
    "tata-sampann-chana-dal": None,

    # ── TEA ───────────────────────────────────────────────────────────────
    "tata-tea-gold-rich-taste-leaf-dust": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/ciw/2026/2/18/"
        "bf79f8d0-dfcb-4ebb-be63-b3e291656666_Q5AIG72TKQ_MN_18022026.png"
    ),
    # Tata Tea Premium is a DIFFERENT tea — must NOT share Tata Tea Gold image
    "tata-tea-premium-desh-ki-chai": None,
    "brooke-bond-red-label-tea": None,
    "brooke-bond-taj-mahal-tea": None,

    # ── COFFEE ────────────────────────────────────────────────────────────
    "nescafe-classic-instant-coffee-jar": None,
    "bru-instant-coffee-chicory-mix": None,

    # ── BEVERAGES ─────────────────────────────────────────────────────────
    "coca-cola-original-taste-soft-drink": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/CIW/2025/11/28/"
        "28d03859-da45-4e2f-bb4a-4c3079700855_204.png"
    ),
    # Pepsi and Sprite are DIFFERENT brands — must NOT use Coca-Cola image
    "pepsi-cola-soft-drink": None,
    "sprite-lime-flavoured-cold-drink": None,
    "real-fruit-power-mixed-fruit-juice": None,
    "frooti-fresh-mango-drink": None,
    "paper-boat-aamras-mango-fruit-juice": None,

    # ── NOODLES ───────────────────────────────────────────────────────────
    "maggi-2-minute-masala-noodles": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/CIW/2026/5/20/"
        "682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"
    ),
    # Maggi Veg Atta Noodles is a different product — must NOT share 2-Minute Masala image
    "maggi-veg-atta-noodles": None,
    "sunfeast-yippee-magic-masala-noodles": None,
    "nissin-cup-noodles-veggie-manchow": None,

    # ── BISCUITS / SNACKS ─────────────────────────────────────────────────
    "parle-g-original-glucose-biscuits": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/ciw/2025/12/18/"
        "f32e2bf5-96eb-472e-b732-70153306008c_HEDSJ4MV73_MN_17122025.png"
    ),
    # Britannia Good Day is a DIFFERENT brand/product — must NOT share Parle-G image
    "britannia-good-day-cashew-cookies": None,
    "britannia-bourbon-chocolate-cream": None,
    "britannia-marie-gold-biscuits": None,
    "cadbury-oreo-vanilla-creme-cookies": None,
    "parle-hide-seek-chocolate-chip-cookies": None,
    "lays-indias-magic-masala-potato-chips": (
        "https://media-assets.swiggy.com/swiggy/image/upload/"
        "NI_CATALOG/IMAGES/CIW/2026/3/18/"
        "684c1fe7-260e-41c1-b0b5-2af8499f1fb8_297695_1.png"
    ),
    # Lay's Classic Salted is a different flavour — must NOT share Magic Masala image
    "lays-classic-salted-potato-chips": None,
    "kurkure-masala-munch-crisps": None,
    "haldirams-nagpur-bhujia-sev": None,
    "haldirams-aloo-bhujia": None,
    "cadbury-dairy-milk-silk-chocolate-bar": None,
    "bingo-mad-angles-achaari-masti": None,

    # ── CLEANING ──────────────────────────────────────────────────────────
    "surf-excel-matic-front-load-detergent-powder": None,
    # Surf Excel Easy Wash is DIFFERENT from Surf Excel Matic — must NOT share image
    "surf-excel-easy-wash-detergent-powder": None,
    "ariel-matic-front-load-detergent": None,
    "vim-dishwash-liquid-gel-lemon": None,
    # Vim Dishwash Bar is DIFFERENT from Vim Liquid Gel — must NOT share image
    "vim-dishwash-bar-with-polycoat": None,
    "lizol-disinfectant-floor-cleaner-citrus": None,
    "harpic-power-plus-toilet-cleaner-original": None,
    "origami-so-soft-kitchen-towels": None,
    "shalimar-heavy-duty-garbage-bags": None,

    # ── PERSONAL CARE ─────────────────────────────────────────────────────
    "dettol-original-bathing-soap": None,
    # Dettol Handwash Refill is DIFFERENT from Dettol Soap — must NOT share image
    "dettol-liquid-handwash-refill-pouch": None,
    "dove-cream-beauty-bathing-bar": None,
    "head-shoulders-anti-dandruff-shampoo": None,
    "sunsilk-black-shine-shampoo": None,
    "colgate-total-dental-plaque-toothpaste": None,
    # Colgate MaxFresh is DIFFERENT from Colgate Total — must NOT share image
    "colgate-maxfresh-spicy-fresh-red-gel": None,
    "sensodyne-rapid-relief-toothpaste": None,

    # ── SPICES ────────────────────────────────────────────────────────────
    "everest-turmeric-powder": None,
    "mdh-deggi-mirch-red-chilli-powder": None,
}


def get_registry_image(product_name: str, brand: Optional[str] = None) -> Optional[str]:
    """
    Look up a product in the canonical image registry.

    Matching strategy (in order):
    1. Exact slug match.
    2. Weighted word-overlap — requires ≥ 3 meaningful words AND at least one
       distinguishing (non-brand) keyword to prevent wrong cross-product matches.
    3. None — never fall back to brand-only matching.

    Returns the URL string (may be None if the product is registered but has no
    confirmed image yet — the frontend will show a clean category placeholder).
    Returns the sentinel ``_NOT_IN_REGISTRY`` for products not matched at all.
    """
    if not product_name:
        return None

    slug = to_slug(product_name)
    if not slug:
        return None

    # 1. Exact match
    if slug in PRODUCT_IMAGE_REGISTRY:
        return PRODUCT_IMAGE_REGISTRY[slug]

    # 2. Word-overlap match
    slug_words = set(slug.split("-")) - _STOP_WORDS
    # meaningful words = all words that aren't brand-level stop-words
    meaningful_slug_words = slug_words - _BRAND_WORDS

    best_key: Optional[str] = None
    best_score = 0

    for key in PRODUCT_IMAGE_REGISTRY:
        key_words = set(key.split("-")) - _STOP_WORDS
        overlap = slug_words & key_words
        meaningful_overlap = overlap - _BRAND_WORDS

        # Must have ≥ 3 total overlapping words AND ≥ 1 meaningful (non-brand) overlap
        if len(overlap) >= 3 and len(meaningful_overlap) >= 1:
            # Penalise matches that only overlap on brand words
            score = len(overlap) + len(meaningful_overlap) * 2
            if score > best_score:
                # Extra safety: ensure the registered slug is a PREFIX or SUFFIX
                # of the target (or vice-versa) — prevents "surf excel matic" from
                # matching "surf excel easy wash" via shared "surf excel" words
                if key in slug or slug in key or slug.startswith(key[:6]):
                    best_score = score
                    best_key = key

    if best_key is not None:
        return PRODUCT_IMAGE_REGISTRY[best_key]

    return None
