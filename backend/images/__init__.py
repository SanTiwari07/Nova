"""
Images package — dynamic product image resolution pipeline.

Priority chain:
  1. Swiggy CDN image URL (if genuinely present in MCP response)
  2. Open Food Facts barcode/GTIN exact match
  3. Open Food Facts brand + name + quantity match (confidence >= threshold)
  4. null  →  imageStatus: "unavailable"

No images are downloaded into the repository.
No AI-generated images are used.
No emoji product imagery is used.
"""
from .image_resolver import ImageResolver
from .image_cache import ImageCache
from .open_food_facts import OpenFoodFactsResolver

__all__ = ["ImageResolver", "ImageCache", "OpenFoodFactsResolver"]
