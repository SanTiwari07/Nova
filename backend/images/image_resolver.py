"""
ImageResolver — orchestrates the full product image resolution pipeline.

Resolution priority (strictly ordered):

  PRIORITY 1 — Swiggy CDN image URL
    If the Swiggy MCP response contains a legitimate HTTPS image URL,
    use it directly. Do not call Open Food Facts.

  PRIORITY 2 — Open Food Facts barcode / GTIN match
    If Swiggy provides a barcode/GTIN/EAN/UPC, use it for an exact
    OFF lookup. Confidence = 1.00.

  PRIORITY 3 — Open Food Facts brand + name + quantity match
    Attempt a controlled identity search. Requires confidence >= threshold.
    Pack size mismatch = hard reject.

  PRIORITY 4 — No confident match
    Return imageUrl = None, imageStatus = "unavailable".
    The UI shows a neutral placeholder. Never substitute an emoji or
    an AI-generated image.

Cache: successful and unavailable resolutions are cached to prevent
repeated OFF API calls for the same product.
"""

import asyncio
import os
from typing import Any, Dict, Optional, Tuple

from .image_cache import image_cache
from .open_food_facts import OpenFoodFactsResolver

# Configurable minimum confidence to display an image
IMAGE_MATCH_THRESHOLD = float(os.environ.get("IMAGE_MATCH_THRESHOLD", "0.90"))

_off_resolver = OpenFoodFactsResolver()


class ImageResolver:
    """
    Entry point for the image resolution pipeline.

    Usage:
        resolver = ImageResolver()
        result = await resolver.resolve(product)

    result shape:
        {
            "imageUrl":        str | None,
            "imageSource":     "swiggy" | "open_food_facts" | "unavailable",
            "imageConfidence": float,      # 0.0 – 1.00
            "imageStatus":     "found" | "unavailable",
        }
    """

    def __init__(self, cache: Optional["ImageCache"] = None):
        """
        :param cache: Optional ImageCache instance. Pass a fresh ImageCache()
                      in tests for isolation. Defaults to the module-level singleton.
        """
        if cache is not None:
            self._cache = cache
        else:
            self._cache = image_cache

    # ── Public API ────────────────────────────────────────────────────────────

    async def resolve(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a real product image for the given product dict.

        product fields used:
            id / variantId / productId  — for cache key
            imageUrl / image            — Swiggy-provided URL (priority 1)
            barcode / gtin / ean / upc  — for OFF barcode lookup (priority 2)
            brand, name, quantity, unit — for OFF identity search (priority 3)
        """
        product_key = self._make_key(product)

        # ── Cache check ──────────────────────────────────────────────────────────────────────
        cached = self._cache.get(product_key)
        if cached:
            return self._to_result(cached)

        # ── Priority 1: Swiggy image URL ────────────────────────────────────────────
        swiggy_url = self._extract_swiggy_url(product)
        if swiggy_url:
            print(
                f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
                f"Source: Swiggy | Image: FOUND"
            )
            record = self._cache.set(
                product_key, swiggy_url, source="swiggy", confidence=1.0,
                matched_identifier="swiggy_cdn"
            )
            return self._to_result(record)

        # ── Priority 2: OFF barcode lookup ─────────────────────────────────────────
        barcode = self._extract_barcode(product)
        if barcode:
            img_url, conf, match_id = await asyncio.get_running_loop().run_in_executor(
                None, _off_resolver.lookup_by_barcode, barcode
            )
            if img_url:
                print(
                    f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
                    f"Source: Open Food Facts | Match: barcode | "
                    f"Confidence: {conf:.2f} | Image: FOUND"
                )
                record = self._cache.set(
                    product_key, img_url, source="open_food_facts",
                    confidence=conf, matched_identifier=match_id
                )
                return self._to_result(record)

        # ── Priority 3: OFF identity search ─────────────────────────────────────────
        name = product.get("name") or ""
        brand = product.get("brand") or None
        quantity = product.get("quantity") or None
        unit = product.get("unit") or None

        if name:
            img_url, conf, match_id = await asyncio.get_running_loop().run_in_executor(
                None,
                _off_resolver.lookup_by_identity,
                name, brand, quantity, unit
            )
            if img_url and conf >= IMAGE_MATCH_THRESHOLD:
                print(
                    f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
                    f"Source: Open Food Facts | Match: identity | "
                    f"Confidence: {conf:.2f} | Image: FOUND"
                )
                record = self._cache.set(
                    product_key, img_url, source="open_food_facts",
                    confidence=conf, matched_identifier=match_id
                )
                return self._to_result(record)

        # ── Priority 4: Unavailable ───────────────────────────────────────────────
        print(
            f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
            f"Image: NOT FOUND"
        )
        record = self._cache.set(
            product_key, None, source="unavailable",
            confidence=0.0, matched_identifier=None
        )
        return self._to_result(record)

    async def resolve_batch(self, products: list) -> list:
        """
        Resolve images for a list of products concurrently.
        Returns the same list with image fields enriched.
        """
        tasks = [self.resolve(p) for p in products]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        enriched = []
        for product, result in zip(products, results):
            if isinstance(result, Exception):
                print(f"[IMAGE RESOLVER] Error resolving image for {product.get('name')}: {result}")
                enriched.append({
                    **product,
                    "imageUrl": None,
                    "imageSource": "unavailable",
                    "imageConfidence": 0.0,
                    "imageStatus": "unavailable",
                })
            else:
                enriched.append({**product, **result})

        return enriched

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_key(self, product: Dict[str, Any]) -> str:
        """
        Build a stable cache key from the product's unique identifier.
        Falls back to name + brand + pack_size if no ID is available.
        """
        pid = (
            product.get("variantId")
            or product.get("id")
            or product.get("productId")
        )
        if pid:
            retailer = product.get("retailer", "swiggy")
            return f"{retailer}:{pid}"

        # Fallback: use normalized product identity string
        name = (product.get("name") or "").lower().strip()
        brand = (product.get("brand") or "").lower().strip()
        qty = product.get("pack_size") or ""
        return f"identity:{brand}:{name}:{qty}"

    def _extract_swiggy_url(self, product: Dict[str, Any]) -> Optional[str]:
        """
        Extract a legitimate Swiggy CDN HTTPS image URL from the product.
        Returns None if no real URL is present — never fabricates one.
        """
        candidates = [
            product.get("imageUrl"),
            product.get("image"),
        ]

        # Also check raw data fields that may have been captured from the MCP response
        raw_data = product.get("rawData") or {}
        variation = raw_data.get("variation") or {}
        raw_product = raw_data.get("product") or {}

        # Inspect ALL known possible field names from the real Swiggy MCP response
        # (determined empirically — only use if actually present)
        for obj in [variation, raw_product]:
            for field in [
                "imageUrl", "imageURL", "image_url",
                "thumbnail", "thumbnailUrl", "thumbnail_url",
                "media", "mediaUrl", "media_url",
                "image", "images",
            ]:
                val = obj.get(field)
                if isinstance(val, list) and val:
                    val = val[0]
                if val and isinstance(val, str):
                    candidates.append(val)

        for url in candidates:
            if not url or not isinstance(url, str):
                continue
            url = url.strip()
            if not url or url.lower() in ("none", "null", "undefined"):
                continue
            if url.startswith("https://") or url.startswith("http://"):
                return url
            # Swiggy media-assets relative hash path
            if "/" in url or len(url) > 10:
                clean = url.lstrip("/")
                return f"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,w_500/{clean}"

        return None

    def _extract_barcode(self, product: Dict[str, Any]) -> Optional[str]:
        """
        Extract a barcode/GTIN/EAN/UPC from the product if provided by Swiggy.
        Returns None if not present — never constructs one from the product name.
        """
        for field in ["barcode", "gtin", "ean", "upc", "ean13", "ean8", "gtinUpc"]:
            val = product.get(field)
            if val and isinstance(val, (str, int)):
                barcode = str(val).strip()
                if barcode and barcode not in ("0", "null", "none", "undefined"):
                    return barcode

        # Also check raw data
        raw_data = product.get("rawData") or {}
        for obj in [raw_data.get("variation") or {}, raw_data.get("product") or {}]:
            for field in ["barcode", "gtin", "ean", "upc", "ean13", "ean8", "gtinUpc"]:
                val = obj.get(field)
                if val and isinstance(val, (str, int)):
                    barcode = str(val).strip()
                    if barcode and barcode not in ("0", "null", "none", "undefined"):
                        return barcode

        return None

    def _to_result(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a cache record into the standard image resolution result."""
        source = record.get("source", "unavailable")
        image_url = record.get("imageUrl")
        return {
            "imageUrl": image_url,
            "imageSource": source,
            "imageConfidence": record.get("confidence", 0.0),
            "imageStatus": "found" if image_url else "unavailable",
        }


# Singleton
image_resolver = ImageResolver()
