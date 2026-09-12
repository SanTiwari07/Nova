"""
ImageCache — in-memory TTL cache for resolved product image URLs.

Prevents repeated Open Food Facts API calls for the same product.
Cache records include source, confidence, matched identifier and expiry.

No image files are stored locally — only remote URLs are cached.
"""

import time
import os
from typing import Dict, Any, Optional

# Default TTL: 24 hours for successful resolutions, 1 hour for "unavailable"
CACHE_TTL_FOUND = int(os.environ.get("IMAGE_CACHE_TTL_FOUND", str(24 * 3600)))
CACHE_TTL_UNAVAILABLE = int(os.environ.get("IMAGE_CACHE_TTL_UNAVAILABLE", str(3600)))


class ImageCache:
    """
    In-memory image resolution cache.

    Record schema:
    {
        "productKey":        str,    # e.g. "swiggy:spin_maggi_4pk"
        "imageUrl":          str | None,
        "source":            str,    # "swiggy" | "open_food_facts" | "unavailable"
        "confidence":        float,  # 0.0 – 1.0
        "matchedIdentifier": str | None,  # barcode / search key used
        "resolvedAt":        float,  # unix timestamp
        "expiresAt":         float,  # unix timestamp
    }
    """

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, product_key: str) -> Optional[Dict[str, Any]]:
        """
        Return a cached resolution record if it exists and has not expired.
        Returns None on a cache miss or if the entry is stale.
        """
        record = self._store.get(product_key)
        if not record:
            return None

        if time.time() > record.get("expiresAt", 0):
            # Expired — evict and return miss
            del self._store[product_key]
            print(f"[ImageCache] EXPIRED — evicting key: {product_key}")
            return None

        print(
            f"[ImageCache] HIT — key: {product_key} | "
            f"source: {record.get('source')} | "
            f"confidence: {record.get('confidence', 0):.2f}"
        )
        return record

    def set(
        self,
        product_key: str,
        image_url: Optional[str],
        source: str,
        confidence: float,
        matched_identifier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Store a resolved image URL (or null / unavailable) in the cache.
        TTL differs for successful vs unsuccessful resolutions.
        """
        now = time.time()
        ttl = CACHE_TTL_FOUND if image_url else CACHE_TTL_UNAVAILABLE

        record: Dict[str, Any] = {
            "productKey": product_key,
            "imageUrl": image_url,
            "source": source,
            "confidence": confidence,
            "matchedIdentifier": matched_identifier,
            "resolvedAt": now,
            "expiresAt": now + ttl,
        }
        self._store[product_key] = record

        print(
            f"[ImageCache] SET — key: {product_key} | "
            f"source: {source} | "
            f"confidence: {confidence:.2f} | "
            f"url: {'yes' if image_url else 'null'} | "
            f"ttl: {ttl}s"
        )
        return record

    def invalidate(self, product_key: str) -> None:
        """Remove a single key from the cache."""
        if product_key in self._store:
            del self._store[product_key]
            print(f"[ImageCache] INVALIDATED — key: {product_key}")

    def clear(self) -> None:
        """Flush the entire cache."""
        self._store.clear()
        print("[ImageCache] CLEARED")

    def stats(self) -> Dict[str, Any]:
        """Return cache statistics for observability."""
        now = time.time()
        valid = [r for r in self._store.values() if r.get("expiresAt", 0) > now]
        sources: Dict[str, int] = {}
        for r in valid:
            s = r.get("source", "unknown")
            sources[s] = sources.get(s, 0) + 1

        return {
            "total_entries": len(self._store),
            "valid_entries": len(valid),
            "sources": sources,
        }


# Singleton — shared across the process lifetime
image_cache = ImageCache()
