"""
DEPRECATED: Hardcoded fallback assets (/assets/fallbacks/*.webp) are completely removed
per Household Autopilot specification.
All dynamic product image resolution is performed by ImageResolver (backend/images/image_resolver.py)
querying Open Food Facts and Swiggy CDN.
"""
print("Notice: Hardcoded fallback enrichment is deprecated. Use ImageResolver for real image lookups.")

