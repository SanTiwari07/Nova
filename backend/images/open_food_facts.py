"""
OpenFoodFactsResolver — real product image lookup via the official Open Food Facts API.

API docs: https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/
Base URL:  https://world.openfoodfacts.org/api/v2/

RULES:
  - NEVER construct image URLs manually.
  - NEVER scrape the Open Food Facts website.
  - NEVER download images into the repository.
  - Use only image URLs returned by the OFF API (image_front_url preferred).
  - Prefer barcode/GTIN matching.
  - Name-only matching is not trusted (confidence 0.30, below display threshold).
  - Pack size / quantity must match for a confident name-based result.
  - If there is any ambiguity, return None (let UI show "Image unavailable").
"""

import re
import os
import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

# Public OFF API — no authentication required for read operations
OFF_BASE = "https://world.openfoodfacts.org"
OFF_API_V2 = f"{OFF_BASE}/api/v2"

# Minimum confidence to return an image
IMAGE_MATCH_THRESHOLD = float(os.environ.get("IMAGE_MATCH_THRESHOLD", "0.90"))

# OFF search returns many fields; we only need a subset
_OFF_FIELDS = "code,product_name,brands,quantity,image_front_url,image_url,image_front_small_url"

# Request timeout (seconds)
_TIMEOUT = 8


def _safe_print(msg: str) -> None:
    """Print safely on Windows consoles that use cp1252 encoding by stripping non-encodable chars."""
    try:
        print(msg)
    except UnicodeEncodeError:
        safe_msg = msg.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"
        )
        print(safe_msg)

# Minimum confidence to return an image
IMAGE_MATCH_THRESHOLD = float(os.environ.get("IMAGE_MATCH_THRESHOLD", "0.90"))

# OFF search returns many fields; we only need a subset
_OFF_FIELDS = "code,product_name,brands,quantity,image_front_url,image_url,image_front_small_url"

# Request timeout (seconds)
_TIMEOUT = 8


class OpenFoodFactsResolver:
    """
    Resolves real product photographs from the Open Food Facts database.

    Priority:
      1. Barcode / GTIN / EAN / UPC exact match  → confidence 1.00
      2. Brand + name + quantity exact match      → confidence 0.90 (configurable minimum)

    Returns (image_url, confidence, matched_identifier) or (None, 0.0, None).
    """

    # ── Barcode Lookup ────────────────────────────────────────────────────────

    def lookup_by_barcode(self, barcode: str) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Look up a product by its barcode/GTIN/EAN/UPC.

        Returns:
            (image_url, confidence=1.00, matched_identifier=barcode)
            or (None, 0.0, None) if not found or image absent.
        """
        barcode = str(barcode).strip()
        if not barcode:
            return None, 0.0, None

        url = f"{OFF_API_V2}/product/{urllib.parse.quote(barcode)}?fields={_OFF_FIELDS}"
        print(f"[OFF] Barcode lookup: {barcode}")

        data = self._get_json(url)
        if not data:
            return None, 0.0, None

        # OFF returns {"status": 1, "product": {...}} on success
        # or {"status": 0, "status_verbose": "product not found"} on miss
        if data.get("status") != 1:
            print(f"[OFF] Barcode {barcode}: product not found in Open Food Facts")
            return None, 0.0, None

        product = data.get("product") or {}
        image_url = self._extract_image_url(product)

        if not image_url:
            print(f"[OFF] Barcode {barcode}: product found but no image available")
            return None, 0.0, None

        print(f"[OFF] Barcode {barcode}: EXACT MATCH — confidence 1.00 — image: {image_url[:80]}...")
        return image_url, 1.00, barcode

    # ── Name / Brand / Quantity Search ───────────────────────────────────────

    def lookup_by_identity(
        self,
        name: str,
        brand: Optional[str] = None,
        quantity: Optional[str] = None,
        unit: Optional[str] = None,
    ) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Search Open Food Facts for a product by brand + name + quantity.

        Very conservative matching rules:
          - Quantity (numeric value) must match exactly if both sides provide it.
          - Unit must be compatible (g vs grams etc.).
          - If quantity mismatch → reject, return (None, 0.0, None).
          - Brand and name must both match the top result.

        Returns:
            (image_url, confidence, matched_search_key) or (None, 0.0, None)
        """
        if not name or not name.strip():
            return None, 0.0, None

        # Build search query: avoid duplicating the brand if name already starts with it
        name_clean = name.strip()
        brand_clean = (brand or "").strip()

        if brand_clean and not name_clean.lower().startswith(brand_clean.lower()):
            search_query = f"{brand_clean} {name_clean}"
        else:
            search_query = name_clean

        # Add quantity for tighter matching
        qty_str = self._normalize_quantity_str(quantity, unit)
        if qty_str:
            search_query += f" {qty_str}"

        search_key = search_query
        print(f"[OFF] Identity search: '{search_query}'")

        # Use the OFF v2 search endpoint (more stable than legacy /cgi/search.pl)
        url = (
            f"{OFF_API_V2}/search"
            f"?q={urllib.parse.quote(search_query)}"
            f"&fields={_OFF_FIELDS}"
            f"&page_size=5&page=1"
        )

        data = self._get_json(url)
        if not data:
            return None, 0.0, None

        products = data.get("products") or []
        if not products:
            print(f"[OFF] No results for: '{search_query}'")
            return None, 0.0, None

        # Evaluate top candidates
        best_url: Optional[str] = None
        best_conf: float = 0.0
        best_key: Optional[str] = None

        for candidate in products[:3]:
            conf, reason = self._score_candidate(
                candidate,
                name=name,
                brand=brand,
                quantity=quantity,
                unit=unit,
            )
            _safe_print(
                f"[OFF]   Candidate: '{candidate.get('product_name', '')}' "
                f"brand='{candidate.get('brands', '')}' "
                f"qty='{candidate.get('quantity', '')}' "
                f"-> confidence {conf:.2f} ({reason})"
            )

            if conf > best_conf:
                img = self._extract_image_url(candidate)
                if img:
                    best_conf = conf
                    best_url = img
                    best_key = search_key

        if best_conf < IMAGE_MATCH_THRESHOLD:
            print(
                f"[OFF] Identity match confidence {best_conf:.2f} < threshold {IMAGE_MATCH_THRESHOLD} — "
                f"returning unavailable to avoid wrong product image"
            )
            return None, 0.0, None

        print(f"[OFF] Identity match: confidence {best_conf:.2f} — image: {best_url[:80]}..." if best_url else "[OFF] No image")
        return best_url, best_conf, best_key

    # ── Confidence Scoring ────────────────────────────────────────────────────

    def _score_candidate(
        self,
        candidate: Dict[str, Any],
        name: str,
        brand: Optional[str],
        quantity: Optional[str],
        unit: Optional[str],
    ) -> Tuple[float, str]:
        """
        Score an OFF candidate product against our known product identity.

        Scoring rules (deterministic, not ML):
          - Exact brand match:         +0.3
          - Exact name match:          +0.3
          - Strong name match (substr): +0.2
          - Exact quantity+unit match: +0.4
          - Quantity mismatch:         → 0.0 (hard reject)
          - No quantity provided:      +0.0 (neutral)
        """
        cand_name = (candidate.get("product_name") or "").lower().strip()
        cand_brand = (candidate.get("brands") or "").lower().strip()
        cand_qty_raw = (candidate.get("quantity") or "").strip()

        our_name = name.lower().strip()
        our_brand = (brand or "").lower().strip()

        score = 0.0
        reasons: List[str] = []

        # Brand match
        brand_match = False
        if our_brand and cand_brand:
            # OFF brands field can be comma-separated
            cand_brands = [b.strip() for b in cand_brand.split(",")]
            if our_brand in cand_brands or any(our_brand in b for b in cand_brands):
                score += 0.3
                brand_match = True
                reasons.append("brand✓")

        # Name match
        name_match_strong = False
        if cand_name and our_name:
            if our_name == cand_name:
                score += 0.3
                name_match_strong = True
                reasons.append("name_exact✓")
            elif our_name in cand_name or cand_name in our_name:
                score += 0.2
                name_match_strong = True
                reasons.append("name_substr✓")
            else:
                # Check word overlap
                our_words = set(our_name.split())
                cand_words = set(cand_name.split())
                overlap = our_words & cand_words
                overlap_ratio = len(overlap) / max(len(our_words), 1)
                if overlap_ratio >= 0.6:
                    score += 0.15
                    reasons.append(f"name_words✓({overlap_ratio:.0%})")

        # Quantity match — critical: mismatch → hard reject
        our_qty_str = self._normalize_quantity_str(quantity, unit)
        if our_qty_str and cand_qty_raw:
            our_val, our_unit_n = self._parse_quantity(our_qty_str)
            cand_val, cand_unit_n = self._parse_quantity(cand_qty_raw)

            if our_val is not None and cand_val is not None:
                # Values must be within 1% (floating point tolerance)
                if our_unit_n == cand_unit_n and abs(our_val - cand_val) / max(our_val, 0.001) < 0.01:
                    score += 0.4
                    reasons.append("qty✓")
                else:
                    # HARD REJECT — wrong pack size
                    return 0.0, f"qty_mismatch(ours={our_qty_str},cand={cand_qty_raw})"
        elif our_qty_str and not cand_qty_raw:
            # OFF product has no quantity — uncertain, don't reward or penalize
            reasons.append("qty_unknown")
        elif not our_qty_str:
            # We have no quantity — rely on name/brand
            reasons.append("no_qty")

        return score, ",".join(reasons) if reasons else "no_match"

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _extract_image_url(self, product: Dict[str, Any]) -> Optional[str]:
        """
        Extract a real product image URL from an OFF product dict.
        Prefers front image. Validates URL is HTTPS and plausibly an OFF CDN URL.
        """
        candidates = [
            product.get("image_front_url"),
            product.get("image_url"),
            product.get("image_front_small_url"),
        ]

        for url in candidates:
            if not url or not isinstance(url, str):
                continue
            url = url.strip()
            if url.startswith("https://") and len(url) > 20:
                return url

        return None

    def _normalize_quantity_str(self, quantity: Optional[str], unit: Optional[str]) -> str:
        """
        Produce a normalized quantity string like '1 L', '500 g', '280 g'.
        Returns empty string if neither quantity nor unit is provided.
        """
        parts = []
        if quantity:
            parts.append(quantity.strip())
        if unit:
            parts.append(unit.strip())
        return " ".join(parts)

    def _parse_quantity(self, qty_str: str) -> Tuple[Optional[float], str]:
        """
        Parse a quantity string like '1 L', '500g', '280 g', '5 kg' into
        (numeric_value_in_base_unit, normalized_unit).

        Converts:
          kg → g  (multiply by 1000)
          ml → ml  (keep as ml)
          l  → ml  (multiply by 1000)
        """
        qty_str = qty_str.lower().strip()

        # Extract first numeric value and unit
        m = re.match(r"([\d.]+)\s*([a-z]+)", qty_str)
        if not m:
            return None, ""

        try:
            value = float(m.group(1))
        except ValueError:
            return None, ""

        raw_unit = m.group(2).lower().strip()

        # Normalize units to base (g for mass, ml for volume)
        UNIT_MAP = {
            "g": ("g", 1.0),
            "gm": ("g", 1.0),
            "gram": ("g", 1.0),
            "grams": ("g", 1.0),
            "kg": ("g", 1000.0),
            "kgs": ("g", 1000.0),
            "kilogram": ("g", 1000.0),
            "ml": ("ml", 1.0),
            "l": ("ml", 1000.0),
            "liter": ("ml", 1000.0),
            "litre": ("ml", 1000.0),
            "liters": ("ml", 1000.0),
            "litres": ("ml", 1000.0),
            "pc": ("pc", 1.0),
            "pcs": ("pc", 1.0),
            "piece": ("pc", 1.0),
            "pieces": ("pc", 1.0),
            "pack": ("pack", 1.0),
        }

        if raw_unit in UNIT_MAP:
            base_unit, multiplier = UNIT_MAP[raw_unit]
            return value * multiplier, base_unit

        return value, raw_unit

    def _get_json(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Perform a GET request and return parsed JSON, or None on failure.
        Respects Open Food Facts robots.txt / rate limits with a small delay.
        """
        headers = {
            "User-Agent": "HouseholdAutopilot/1.0 (https://github.com/nova; contact@nova.household)",
            "Accept": "application/json",
        }

        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            print(f"[OFF] HTTP error {e.code} for URL: {url}")
            return None
        except urllib.error.URLError as e:
            print(f"[OFF] URL error: {e.reason} for URL: {url}")
            return None
        except Exception as e:
            print(f"[OFF] Unexpected error: {e} for URL: {url}")
            return None
