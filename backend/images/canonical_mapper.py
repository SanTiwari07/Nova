import re
from typing import Dict, Optional, Any


def normalize_product_name(name: str) -> str:
    """
    Normalize a product name for family-level matching.
    Strips size/weight tokens, punctuation, and excess whitespace.
    """
    if not name:
        return ""

    name = name.lower()
    # Replace common separators and punctuation with space
    name = re.sub(r'[-/()\\[\\]{}+&]+', ' ', name)

    # Remove size/quantity tokens
    # e.g., 100 g, 250 g, 500 g, 1 kg, 2 kg, 100 ml, 1 L, 6 pcs, pack of 2
    qty_pattern = (
        r'\b\d+(?:\.\d+)?\s*'
        r'(?:kg|g|gm|gram|grams|mg|ml|l|liter|litre|liters|litres|'
        r'pcs|pc|pieces|piece|pack|packet|count|rolls|roll|tabs|tab|'
        r'pouch|pouches|bottle|bottles|can|cans|cup|cups|bar|bars)\b'
    )
    name = re.sub(qty_pattern, ' ', name)
    name = re.sub(r'\bpack of \d+\b', ' ', name)

    # Clean up duplicate spaces
    name = re.sub(r'\s+', ' ', name).strip()
    return name


# ---------------------------------------------------------------------------
# Words that MUST NOT be the sole basis for a family match.
# If the only shared words are these, the match is rejected.
# ---------------------------------------------------------------------------
_BRAND_ONLY_WORDS = {
    'surf', 'excel', 'ariel', 'vim', 'lizol', 'harpic',
    'amul', 'tata', 'fortune', 'saffola', 'aashirvaad',
    'india', 'gate', 'maggi', 'parle', 'britannia',
    'lays', 'colgate', 'dettol', 'dove', 'head', 'shoulders',
    'nescafe', 'bru', 'brooke', 'bond', 'pepsi', 'sprite',
    'coca', 'cola', 'haldiram', 'haldirams', 'kurkure',
    'cadbury', 'oreo', 'bingo', 'dhara', 'madhur', 'sensodyne',
    'everest', 'mdh', 'daawat', 'kohinoor', 'nissin', 'sunfeast',
    'yippee', 'frooti', 'real', 'paper', 'boat',
}


def get_canonical_image(product_name: str, brand: Optional[str], repo: Any) -> Optional[str]:
    """
    Resolve a product-family image.

    Priority:
    1. Canonical image registry (deterministic, size-independent)
    2. Exact normalized name match in catalog
    3. Hardened substring match (requires ≥ 3 words overlap AND ≥ 1 non-brand word)
    4. None (never brand-only fallback)
    """
    if not product_name:
        return None

    # ── Priority 1: Registry ─────────────────────────────────────────────────
    try:
        from images.product_image_registry import get_registry_image
        registry_url = get_registry_image(product_name, brand)
        if registry_url is not None:
            return registry_url
        # If registry returned None (explicitly registered but no URL), don't
        # continue to catalog fuzzy matching — the registry is the authority.
        # We only fall through if get_registry_image returned None because the
        # product wasn't found in the registry at all.
    except Exception:
        pass

    norm_target = normalize_product_name(product_name)
    if not norm_target:
        return None

    # ── Priority 2 & 3: Catalog matching ────────────────────────────────────
    canonical_map: Dict[str, str] = {}
    for p in repo.products:
        img = p.get("imageUrl")
        if img:
            p_name = p.get("name", "")
            norm_p = normalize_product_name(p_name)
            if norm_p and norm_p not in canonical_map:
                canonical_map[norm_p] = img

    # 2. Exact canonical product-family match
    if norm_target in canonical_map:
        return canonical_map[norm_target]

    # 3. Hardened substring match
    target_words = set(norm_target.split())
    best_match = None
    max_overlap = 0

    for mapped_name, img in canonical_map.items():
        mapped_words = set(mapped_name.split())
        overlap = target_words & mapped_words
        non_brand_overlap = overlap - _BRAND_ONLY_WORDS

        # Require ≥ 3 total overlapping words AND ≥ 1 non-brand distinguishing word.
        # This prevents "Surf Excel Easy Wash" from wrongly matching
        # "Surf Excel Matic Front Load" (they share "surf excel" = 2 words, no non-brand overlap).
        if len(overlap) >= 3 and len(non_brand_overlap) >= 1:
            # Also require one name to be a proper prefix/substring of the other
            if mapped_name in norm_target or norm_target in mapped_name:
                if len(overlap) > max_overlap:
                    max_overlap = len(overlap)
                    best_match = img

    return best_match
