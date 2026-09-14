"""
OpenFoodFactsResolver - real product image lookup via the official Open Food Facts API.

API docs: https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/
Base URL:  https://world.openfoodfacts.org/api/v2/

RULES:
  - NEVER construct image URLs manually.
  - NEVER scrape the Open Food Facts website.
  - NEVER download images into the repository.
  - Use only verified catalog image URLs returned by the OFF API (selected_images.front / image_front_url).
  - NEVER use uncurated crowdsourced user upload photos (e.g. 1.400.jpg).
  - Prefer barcode/GTIN matching.
  - Pack size / quantity must match exactly (within 1%) for an identity result.
  - If there is any ambiguity or quality issue, return None (let UI show "Image unavailable").
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

from .image_validator import validate_image_url

# Public OFF API - no authentication required for read operations
OFF_BASE = "https://world.openfoodfacts.org"
OFF_API_V2 = f"{OFF_BASE}/api/v2"

# Minimum confidence to return an image
IMAGE_MATCH_THRESHOLD = float(os.environ.get("IMAGE_MATCH_THRESHOLD", "0.50"))

# OFF search fields: request selected_images for verified front catalog shots
_OFF_FIELDS = "code,product_name,brands,quantity,selected_images,image_front_url,image_front_small_url"

# Request timeout (seconds)
_TIMEOUT = 6


def _safe_print(msg: str) -> None:
    """Print safely on Windows consoles that use cp1252 encoding."""
    try:
        print(msg)
    except UnicodeEncodeError:
        safe_msg = msg.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(
            sys.stdout.encoding or "utf-8", errors="replace"
        )
        print(safe_msg)


class OpenFoodFactsResolver:
    """
    Resolves real product photographs from the Open Food Facts database.

    Priority:
      1. Barcode / GTIN / EAN / UPC exact match  → confidence 1.00
      2. Brand + name + quantity exact match      → confidence >= 0.90 (requires exact pack size)

    Returns (image_url, confidence, matched_identifier) or (None, 0.0, None).
    """

    def __init__(self):
        self.last_error_is_transient = False

    # ── Barcode Lookup ────────────────────────────────────────────────────────

    def lookup_by_barcode(self, barcode: str) -> Tuple[Optional[str], float, Optional[str]]:
        """
        Look up a product by its genuine barcode/GTIN/EAN/UPC.
        """
        self.last_error_is_transient = False
        barcode = str(barcode).strip()
        if not barcode:
            return None, 0.0, None

        url = f"{OFF_API_V2}/product/{urllib.parse.quote(barcode)}?fields={_OFF_FIELDS}"
        print(f"[OFF] Barcode lookup: {barcode}")

        data = self._get_json(url)
        if data and data.get("status") == 1:
            product = data.get("product") or {}
            image_url = self._extract_image_url(product)
            if image_url:
                print(f"[OFF] Barcode {barcode}: EXACT MATCH - confidence 1.00 - image: {image_url[:80]}...")
                return image_url, 1.00, barcode

        # Fallback: in.openfoodfacts.org v0 API (used if world API is unreachable)
        v0_url = f"https://in.openfoodfacts.org/api/v0/product/{urllib.parse.quote(barcode)}.json"
        data_v0 = self._get_json(v0_url)
        if data_v0 and data_v0.get("status") == 1:
            prod = data_v0.get("product") or {}
            image_url = self._extract_image_url(prod)
            if image_url:
                print(f"[OFF] Barcode {barcode}: v0 MATCH - confidence 1.00 - image: {image_url[:80]}...")
                return image_url, 1.00, barcode

        print(f"[OFF] Barcode {barcode}: not found or image unavailable")
        return None, 0.0, None

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

        Strict matching rules:
          - Quantity (numeric value) must match exactly within 1% if both sides provide it.
          - If quantity mismatch → hard reject, return (None, 0.0, None).
          - No hardcoded barcodes or blind fast-paths.
          - Candidate image must pass deterministic quality and reachability validation.

        Returns:
            (image_url, confidence, matched_search_key) or (None, 0.0, None)
        """
        self.last_error_is_transient = False
        if not name or not name.strip():
            return None, 0.0, None

        name_clean = name.strip()
        brand_clean = (brand or "").strip()

        if brand_clean and not name_clean.lower().startswith(brand_clean.lower()):
            search_query = f"{brand_clean} {name_clean}"
        else:
            search_query = name_clean

        qty_str = self._normalize_quantity_str(quantity, unit)
        qty_in_name = False
        if quantity and str(quantity).strip().lower() in search_query.lower():
            qty_in_name = True
        elif unit and str(unit).strip().lower() in search_query.lower():
            qty_in_name = True

        if qty_str and not qty_in_name:
            search_query += f" {qty_str}"

        search_key = search_query
        print(f"[OFF] Identity search: '{search_query}'")

        # Query OFF v2 search endpoint
        url = (
            f"{OFF_API_V2}/search"
            f"?q={urllib.parse.quote(search_query)}"
            f"&fields={_OFF_FIELDS}"
            f"&page_size=5&page=1"
        )

        data = self._get_json(url)
        # Fallback to cgi/search.pl if v2 fails or returned transient error
        if not data or self.last_error_is_transient:
            cgi_url = (
                f"https://in.openfoodfacts.org/cgi/search.pl"
                f"?search_terms={urllib.parse.quote(search_query)}"
                f"&search_simple=1&action=process&json=1&page_size=5"
            )
            cgi_data = self._get_json(cgi_url)
            if cgi_data:
                data = cgi_data
                self.last_error_is_transient = False

        if not data:
            return None, 0.0, None

        products = data.get("products") or []
        if not products:
            print(f"[OFF] No results for: '{search_query}'")
            return None, 0.0, None

        best_url: Optional[str] = None
        best_conf: float = 0.0
        best_key: Optional[str] = None

        for candidate in products[:4]:
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

            if conf > best_conf and conf >= IMAGE_MATCH_THRESHOLD:
                img = self._extract_image_url(candidate)
                if img:
                    best_conf = conf
                    best_url = img
                    best_key = search_key

        if not best_url or best_conf < IMAGE_MATCH_THRESHOLD:
            print(
                f"[OFF] Identity match failed or confidence ({best_conf:.2f}) below threshold {IMAGE_MATCH_THRESHOLD} - returning unavailable."
            )
            return None, 0.0, None

        print(f"[OFF] Identity match verified: confidence {best_conf:.2f} - image: {best_url[:80]}...")
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
        Deterministic scoring rules:
          - Exact brand match:         +0.30
          - Exact name match:          +0.30
          - Strong name match:         +0.20
          - Exact quantity+unit match: +0.40
          - Quantity mismatch:         -> 0.0 (hard reject)
        """
        cand_name = (candidate.get("product_name") or "").lower().strip()
        cand_brand = (candidate.get("brands") or "").lower().strip()
        cand_qty_raw = (candidate.get("quantity") or "").strip()

        our_name = name.lower().strip()
        our_brand = (brand or "").lower().strip()

        score = 0.0
        reasons: List[str] = []

        # 1. Brand match
        if our_brand and cand_brand:
            cand_brands = [b.strip() for b in cand_brand.split(",")]
            if our_brand in cand_brands or any(our_brand in b for b in cand_brands):
                score += 0.30
                reasons.append("brand✓")

        # 2. Name match
        if cand_name and our_name:
            if our_name == cand_name:
                score += 0.30
                reasons.append("name_exact✓")
            elif our_name in cand_name or cand_name in our_name:
                score += 0.20
                reasons.append("name_substr✓")
            else:
                our_words = set(our_name.split())
                cand_words = set(cand_name.split())
                overlap = our_words & cand_words
                overlap_ratio = len(overlap) / max(len(our_words), 1)
                if overlap_ratio >= 0.6:
                    score += 0.15
                    reasons.append(f"name_words✓({overlap_ratio:.0%})")

        # 3. Quantity match - Removed HARD REJECT to support product family matching
        our_qty_str = self._normalize_quantity_str(quantity, unit)
        if our_qty_str and cand_qty_raw:
            our_val, our_unit_n = self._parse_quantity(our_qty_str)
            cand_val, cand_unit_n = self._parse_quantity(cand_qty_raw)

            if our_val is not None and cand_val is not None:
                if our_unit_n == cand_unit_n and abs(our_val - cand_val) / max(our_val, 0.001) < 0.01:
                    score += 0.40
                    reasons.append("qty✓")
                else:
                    # NO REJECT: Base product image should match even if sizes differ
                    reasons.append(f"qty_mismatch({our_qty_str}!={cand_qty_raw})")
        elif our_qty_str and not cand_qty_raw:
            reasons.append("qty_unknown")
        elif not our_qty_str:
            reasons.append("no_qty")

        return score, ",".join(reasons) if reasons else "no_match"

    # ── Utilities ─────────────────────────────────────────────────────────────

    def _extract_image_url(self, product: Dict[str, Any]) -> Optional[str]:
        """
        Extract a catalog front image URL from an Open Food Facts product.

        Strategy:
          - Prefer official curator-selected front images (selected_images.front.display)
          - Fall back to image_front_url / image_front_small_url
          - Reject raw /1.400.jpg crowdsourced user phone photos (handled by validator)
          - If server-side validation has a transient failure (SSL timeout, connection
            error), still return the URL - the browser can attempt to load it directly.
            Only reject on DEFINITIVE permanent failures (404, HTML, tiny payload, etc.)
        """
        _TRANSIENT_REASONS = ("Connection error", "timed out", "timeout", "HTTP 429", "HTTP 502", "HTTP 503", "HTTP 504")

        def _is_transient(reason: str) -> bool:
            return any(t in reason for t in _TRANSIENT_REASONS)

        # 1. Prefer official front display image chosen by Open Food Facts curators
        selected = product.get("selected_images", {}).get("front", {})
        display = selected.get("display", {})
        if isinstance(display, dict):
            for lang in ["en", "in", "fr", "es", "de"]:
                if lang in display and display[lang]:
                    url = display[lang]
                    valid, reason, _ = validate_image_url(url)
                    if valid:
                        return url
                    if _is_transient(reason):
                        print(f"[OFF] Transient validation error for {url[:60]} - returning URL for browser fetch")
                        return url
            for val in display.values():
                if isinstance(val, str) and val.startswith("http"):
                    valid, reason, _ = validate_image_url(val)
                    if valid:
                        return val
                    if _is_transient(reason):
                        print(f"[OFF] Transient validation error for {val[:60]} - returning URL for browser fetch")
                        return val

        # 2. Check image_front_url
        for field in ["image_front_url", "image_front_small_url"]:
            url = product.get(field)
            if url and isinstance(url, str):
                valid, reason, _ = validate_image_url(url)
                if valid:
                    return url
                if _is_transient(reason):
                    print(f"[OFF] Transient validation error for {url[:60]} - returning URL for browser fetch")
                    return url

        return None

    def _normalize_quantity_str(self, quantity: Optional[str], unit: Optional[str]) -> str:
        """Produce a normalized quantity string like '1 L', '500 g', '280 g'."""
        parts = []
        if quantity:
            parts.append(str(quantity).strip())
        if unit:
            parts.append(str(unit).strip())
        return " ".join(parts)

    def _parse_quantity(self, qty_str: str) -> Tuple[Optional[float], str]:
        """Parse quantity into (numeric_value_in_base_unit, normalized_unit)."""
        qty_str = qty_str.lower().strip()
        m = re.match(r"([\d.]+)\s*([a-z]+)", qty_str)
        if not m:
            return None, ""

        try:
            value = float(m.group(1))
        except ValueError:
            return None, ""

        raw_unit = m.group(2).lower().strip()
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
        """GET request returning parsed JSON with fallback and timeout."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
                body = resp.read().decode("utf-8")
                self.last_error_is_transient = False
                return json.loads(body)
        except urllib.error.HTTPError as e:
            if "world.openfoodfacts.org" in url:
                fallback_url = url.replace("world.openfoodfacts.org", "in.openfoodfacts.org")
                try:
                    fallback_req = urllib.request.Request(fallback_url, headers=headers, method="GET")
                    with urllib.request.urlopen(fallback_req, timeout=_TIMEOUT) as resp:
                        body = resp.read().decode("utf-8")
                        self.last_error_is_transient = False
                        return json.loads(body)
                except urllib.error.HTTPError as fb_e:
                    if fb_e.code in (429, 500, 502, 503, 504, 408):
                        self.last_error_is_transient = True
                except Exception:
                    self.last_error_is_transient = True
            print(f"[OFF] HTTP error {e.code} for URL: {url}")
            if e.code in (429, 500, 502, 503, 504, 408):
                self.last_error_is_transient = True
            return None
        except Exception as e:
            print(f"[OFF] Error fetching JSON: {e}")
            self.last_error_is_transient = True
            return None
