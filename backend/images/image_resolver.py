"""
ImageResolver - orchestrates the full product image resolution pipeline.

Resolution priority (strictly ordered):

  PRIORITY 1 - Genuine Swiggy CDN image URL
    If the product already has a Swiggy CDN imageUrl, return it DIRECTLY
    without any further validation or OFF lookup. The Swiggy CDN is always
    authoritative. Trust it. Pass it straight to the frontend.

  PRIORITY 2 - Swiggy image URL present but not yet validated
    If the Swiggy response contains an imageUrl field and it looks like a
    real CDN URL, validate it and return it if valid. If validation fails
    due to a TRANSIENT error (timeout, SSL, 429/503), still return the URL
    to the browser - let the browser try fetching it directly instead of
    burying the image in a server-side timeout.

  PRIORITY 3 - Open Food Facts barcode / GTIN match
    Only attempted when Swiggy provides NO image at all.
    If Swiggy provides an authentic barcode/GTIN/EAN/UPC, use it for an
    exact OFF lookup. Confidence = 1.00.

  PRIORITY 4 - Open Food Facts brand + name + quantity match
    Attempt a controlled identity search. Requires confidence >= threshold.
    Pack size mismatch = hard reject. Only curated front packaging accepted.

  PRIORITY 5 - No confident match
    Return imageUrl = None, imageStatus = "unavailable".
    The UI shows a clean neutral placeholder ("Image unavailable").
    Never substitute an emoji or an AI-generated image.

Cache: Only successful resolutions and CONFIRMED unavailable results are cached.
TRANSIENT failures (timeout, 429, 503) are NEVER cached as permanent unavailable.
On startup, any stale "unavailable" entries from previous failures are purged.
"""

import asyncio
import os
from typing import Any, Dict, Optional, Tuple

from .image_cache import image_cache
from .open_food_facts import OpenFoodFactsResolver
from .image_validator import validate_image_url

# Configurable minimum confidence to display an image
IMAGE_MATCH_THRESHOLD = float(os.environ.get("IMAGE_MATCH_THRESHOLD", "0.90"))

_off_resolver = OpenFoodFactsResolver()

# Purge stale unavailable entries from any previous server run on module load
image_cache.clear_unavailable()


class ImageResolver:
    """
    Entry point for the image resolution pipeline.

    Usage:
        resolver = ImageResolver()
        result = await resolver.resolve(product)
    """

    def __init__(self, cache: Optional["ImageCache"] = None):
        if cache is not None:
            self._cache = cache
        else:
            self._cache = image_cache

    # ── Public API ────────────────────────────────────────────────────────────

    async def resolve(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a real product image for the given product dict.

        Priority:
          1. Product already has a valid imageUrl (Swiggy CDN) → return directly
          2. Extract and validate Swiggy CDN URL → validate, return if valid
             (on transient failure, still return URL to let browser try directly)
          3. OFF barcode lookup (only if Swiggy has NO image)
          4. OFF identity search (only if Swiggy has NO image)
          5. Confirmed unavailable
        """
        product_key = self._make_key(product)

        # ── Cache check ───────────────────────────────────────────────────────
        cached = self._cache.get(product_key)
        if cached:
            return self._to_result(cached)

        # ── Priority 1 & 2: Swiggy image URL (Primary Source) ─────────────────
        # Swiggy real image → validate → ProductCard
        existing_url = product.get("imageUrl") or product.get("image")
        if not existing_url:
            existing_url = self._extract_swiggy_url(product)

        if existing_url and isinstance(existing_url, str) and existing_url.startswith("http"):
            valid, reason, _ = validate_image_url(existing_url)
            if valid:
                print(
                    f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
                    f"Source: Swiggy (validated) | Image: FOUND"
                )
                record = self._cache.set(
                    product_key, existing_url, source="swiggy", confidence=1.0,
                    matched_identifier="swiggy_cdn"
                )
                return self._to_result(record)
            else:
                is_transient = (
                    "Connection error" in reason or
                    "timed out" in reason.lower() or
                    "timeout" in reason.lower() or
                    "HTTP 429" in reason or
                    "HTTP 502" in reason or
                    "HTTP 503" in reason or
                    "HTTP 504" in reason
                )
                if is_transient:
                    # Transient reachability error from server: pass URL to browser anyway.
                    print(
                        f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
                        f"Source: Swiggy (transient validation note: {reason}) | "
                        f"Passing URL to browser directly"
                    )
                    return {
                        "imageUrl": existing_url,
                        "imageSource": "swiggy",
                        "imageConfidence": 0.85,
                        "imageStatus": "found",
                    }
                else:
                    print(
                        f"[IMAGE RESOLVER] Swiggy candidate definitively failed validation ({reason}): {existing_url}. Falling back to Open Food Facts."
                    )

        # ── Priority 2: Verified Product Image (Catalog fallback) ─────────────
        # If product is in local verified catalog, use its verified genuine image.
        verified_url = self._extract_verified_catalog_image(product)
        if verified_url:
            print(
                f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
                f"Source: Verified Catalog | Image: FOUND"
            )
            record = self._cache.set(
                product_key, verified_url, source="catalog",
                confidence=1.0, matched_identifier="catalog_verified"
            )
            return self._to_result(record)

        # ── No Swiggy / Verified image → fall through to Open Food Facts ──────

        # ── Priority 3: OFF barcode lookup ────────────────────────────────────
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

        # ── Priority 4: OFF identity search ───────────────────────────────────
        name = product.get("name") or ""
        brand = product.get("brand") or None
        quantity = product.get("quantity") or None
        unit = product.get("unit") or None
        pack_size = product.get("pack_size") or None

        if name:
            img_url, conf, match_id = await asyncio.get_running_loop().run_in_executor(
                None,
                _off_resolver.lookup_by_identity,
                name, brand, quantity or pack_size, unit
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

        # ── Priority 5: Confirmed unavailable ──────────────────────────────────
        # Check if an external transient error occurred (429, 503, timeout)
        if getattr(_off_resolver, "last_error_is_transient", False):
            print(
                f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
                f"External service transient failure (OFF 429/503/timeout) - NOT caching unavailable."
            )
            return {
                "imageUrl": None,
                "imageSource": "unavailable",
                "imageConfidence": 0.0,
                "imageStatus": "unavailable",
            }

        # Only cache this if we actually searched and found nothing.
        # This is a confirmed "no image exists" - not a transient failure.
        print(
            f"[IMAGE RESOLVER] Product: {product.get('name', '?')} | "
            f"Image: CONFIRMED UNAVAILABLE (exhausted all sources)"
        )
        record = self._cache.set(
            product_key, None, source="unavailable",
            confidence=0.0, matched_identifier=None
        )
        return self._to_result(record)

    async def resolve_batch(self, products: list) -> list:
        """
        Resolve images for a list of products concurrently.
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
        Build a stable cache key incorporating the specific variant.
        Never use loose generic keywords like 'Maggi' alone.
        """
        pid = (
            product.get("variantId")
            or product.get("id")
            or product.get("productId")
        )
        retailer = product.get("retailer", "swiggy")
        if pid:
            return f"{retailer}:{pid}"

        name = (product.get("name") or "").lower().strip()
        brand = (product.get("brand") or "").lower().strip()
        qty = (product.get("pack_size") or product.get("quantity") or "").strip()
        return f"{retailer}:identity:{brand}:{name}:{qty}"

    def _extract_swiggy_url(self, product: Dict[str, Any]) -> Optional[str]:
        """
        Extract a legitimate Swiggy CDN HTTPS image URL from product or nested rawData fields.
        Returns None if no authentic URL is present.
        """
        raw_data = product.get("rawData") or {}
        variation = raw_data.get("variation") or {}
        raw_product = raw_data.get("product") or {}

        candidates = []
        for obj in [product, variation, raw_product]:
            if not isinstance(obj, dict):
                continue
            for field in [
                "images", "imageUrl", "imageURL", "image_url",
                "imageId", "image_id", "cloudinaryImageId",
                "thumbnail", "thumbnailUrl", "thumbnail_url",
                "media", "mediaUrl", "media_url",
            ]:
                val = obj.get(field)
                if val:
                    candidates.append(val)

        def _resolve(raw: Any) -> Optional[str]:
            if not raw:
                return None
            if isinstance(raw, list):
                for item in raw:
                    res = _resolve(item)
                    if res:
                        return res
                return None
            if isinstance(raw, dict):
                for k in ("url", "imageUrl", "imageURL", "imageId", "image_id", "id", "path", "mediaUrl"):
                    val = raw.get(k)
                    if val:
                        res = _resolve(val)
                        if res:
                            return res
                return None
            if not isinstance(raw, str):
                return None
            s = raw.strip()
            if not s or s.lower() in ("none", "null", "undefined", ""):
                return None
            if s.startswith("//"):
                return f"https:{s}"
            if s.startswith("http://") or s.startswith("https://"):
                return s
            if s.startswith("media-assets.swiggy.com"):
                return f"https://{s}"
            clean = s.lstrip("/")
            if clean.lower().startswith("ciw/"):
                clean = f"NI_CATALOG/IMAGES/{clean}"
            if "swiggy/image/upload" in clean:
                return f"https://media-assets.swiggy.com/{clean}"
            return f"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,w_500/{clean}"

        for cand in candidates:
            res = _resolve(cand)
            if res:
                return res

        return None

    def _extract_barcode(self, product: Dict[str, Any]) -> Optional[str]:
        """Extract authentic barcode/GTIN/EAN/UPC from product if provided by Swiggy."""
        for field in ["barcode", "gtin", "ean", "upc", "ean13", "ean8", "gtinUpc"]:
            val = product.get(field)
            if val and isinstance(val, (str, int)):
                barcode = str(val).strip()
                if barcode and barcode not in ("0", "null", "none", "undefined"):
                    return barcode

        raw_data = product.get("rawData") or {}
        for obj in [raw_data.get("variation") or {}, raw_data.get("product") or {}]:
            for field in ["barcode", "gtin", "ean", "upc", "ean13", "ean8", "gtinUpc"]:
                val = obj.get(field)
                if val and isinstance(val, (str, int)):
                    barcode = str(val).strip()
                    if barcode and barcode not in ("0", "null", "none", "undefined"):
                        return barcode

        return None

    def _extract_verified_catalog_image(self, product: Dict[str, Any]) -> Optional[str]:
        """Check if local verified catalog contains a genuine image for this product."""
        try:
            from catalog.product_repository import ProductRepository
            repo = ProductRepository()
            pid = str(product.get("id") or product.get("productId") or product.get("product_key") or "")
            clean_pid = pid.split(":")[-1] if pid else ""
            if clean_pid:
                item = repo.get_by_id(clean_pid)
                if item and item.get("imageUrl"):
                    return item.get("imageUrl")
            name = (product.get("name") or "").strip().lower()
            if name:
                for p in repo.products:
                    if p.get("imageUrl") and p.get("name", "").strip().lower() == name:
                        return p.get("imageUrl")
        except Exception as e:
            print(f"[IMAGE RESOLVER] Catalog lookup exception: {e}")
        return None

    def _to_result(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a cache record into standard result dict."""
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
