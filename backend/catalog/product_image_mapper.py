from typing import Dict, Any, Optional

def get_product_fallback_image(item: Dict[str, Any]) -> Optional[str]:
    """
    DEPRECATED: Hardcoded fallback assets (/assets/fallbacks/*.webp) are completely removed
    per Household Autopilot specification.
    Returns None so that products without verified images render the clean neutral
    'Image unavailable' UI state instead of fake artwork or emojis.
    """
    return None

