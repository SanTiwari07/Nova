import os
import re
import json
import time
import asyncio
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple
from .interface import CommerceInterface
from .swiggy_oauth import oauth_manager
from images.image_resolver import image_resolver

logger = logging.getLogger("nova.commerce.swiggy")

from catalog.taxonomy import classify_product, CANONICAL_CATEGORIES

SWIGGY_MCP_URL = os.environ.get("SWIGGY_MCP_URL", "https://mcp.swiggy.com/im")
COMMERCE_MODE = os.environ.get("COMMERCE_MODE", "live").lower()


def infer_product_category(name: str, brand: Optional[str] = None, existing_cat: Optional[str] = None) -> Tuple[str, List[str]]:
    """
    Infers the standard UI category and search/shelf tags using canonical deterministic taxonomy.
    Returns: (category, tags)
    """
    info = classify_product(name, brand, existing_cat)
    return info["category"], info["keywords"]


class SwiggyInstamartAdapter(CommerceInterface):
    """
    Official Swiggy Instamart Commerce Adapter.
    Communicates directly with the Swiggy Instamart MCP at https://mcp.swiggy.com/im
    via Model Context Protocol (Streamable HTTP / JSON-RPC 2.0).

    Authenticates using OAuth 2.1 + PKCE tokens managed by SwiggyOAuthManager.
    Strictly prohibits AI-generated or synthetic product images.
    """

    def __init__(self, mcp_url: str = SWIGGY_MCP_URL):
        self.mcp_url = mcp_url
        self.oauth = oauth_manager
        self.carts: Dict[str, List[Dict[str, Any]]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self._catalog_cache: Optional[List[Dict[str, Any]]] = None
        self._catalog_cache_time: float = 0.0
        self._circuit_broken_until: float = 0.0
        self._last_error: Optional[str] = None

    @property
    def is_circuit_broken(self) -> bool:
        return time.time() < self._circuit_broken_until

    @property
    def last_error(self) -> Optional[str]:
        return self._last_error

    @property
    def is_live(self) -> bool:
        """True if authenticated with a real Swiggy OAuth access token and not in mock mode."""
        token = self.oauth.get_access_token()
        return bool(token) and not token.startswith("demo_") and COMMERCE_MODE not in ("mock",)

    def is_authenticated(self) -> bool:
        token = self.oauth.get_access_token()
        return bool(token)

    def is_connected(self) -> bool:
        return self.is_authenticated()

    @property
    def commerce_mode(self) -> str:
        if self.is_live:
            return "live"
        if COMMERCE_MODE == "mock":
            return "mock"
        return "unauthenticated"

    # ── MCP JSON-RPC 2.0 CLIENT ───────────────────────────────────────────────

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Executes a tool on the official Swiggy Instamart MCP server via JSON-RPC 2.0.
        """
        token = self.oauth.get_access_token()
        if not token:
            print(f"[Swiggy MCP] Tool: {tool_name} Authenticated: False (No active token)")
            return None

        # Only skip if explicit mock token is provided
        if token.startswith("demo_"):
            return None

        # Circuit breaker: if live MCP server recently glitched or rate limited, skip remote HTTP call
        if time.time() < self._circuit_broken_until:
            return None

        arguments = arguments or {}
        req_id = int(time.time() * 1000) % 1000000
        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        print(f"[Swiggy MCP] Tool: {tool_name} Arguments: {json.dumps(arguments)} Authenticated: True")
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {token}",
            "User-Agent": "Household-Autopilot/1.0"
        }

        req = urllib.request.Request(self.mcp_url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=2.5) as response:
                status_code = response.status
                if status_code != 200:
                    print(f"[Commerce] Swiggy MCP response status {status_code}. Trip circuit breaker for 60s.")
                    self._circuit_broken_until = time.time() + 60.0
                    return None
                res_body = response.read().decode("utf-8")
                trimmed = res_body.strip()
                if not (trimmed.startswith("{") or trimmed.startswith("[")):
                    print(f"[Commerce] Swiggy MCP returned non-JSON body (service glitch or auth page). Trip circuit breaker for 60s.")
                    self._circuit_broken_until = time.time() + 60.0
                    return None
                res_json = json.loads(res_body)

                # Check for JSON-RPC error
                if "error" in res_json:
                    err = res_json["error"]
                    print(f"[Swiggy MCP] JSON-RPC Error: {err}")
                    return None

                # Extract tool call payload from MCP result
                result = res_json.get("result", {})
                
                # Format 0: Official Swiggy MCP structuredContent
                if isinstance(result, dict) and "structuredContent" in result and result["structuredContent"]:
                    return result["structuredContent"]

                # Format 1: MCP content blocks [{type: "text", text: "..."}]
                if isinstance(result, dict) and "content" in result:
                    for block in result["content"]:
                        if block.get("type") == "text":
                            try:
                                return json.loads(block.get("text", "{}"))
                            except Exception:
                                return {"raw_text": block.get("text")}

                # Format 2: Direct data payload
                if isinstance(result, dict) and "data" in result:
                    return result["data"]

                if isinstance(result, dict) and result:
                    return result

                return res_json

        except urllib.error.HTTPError as e:
            if e.code == 401:
                print(f"[Swiggy MCP] 401 Unauthorized - token expired or revoked. Clearing session.")
                self.oauth.clear_session()
                self._last_error = "Swiggy Instamart session expired (HTTP 401). Please reconnect."
            elif e.code == 403:
                err_msg = e.read().decode("utf-8", errors="replace")
                summary = err_msg[:120].replace("\n", " ").strip()
                print(f"[Swiggy MCP] 403 Forbidden: {summary}. Keeping session active, setting circuit breaker.")
                self._circuit_broken_until = time.time() + 60.0
                self._last_error = "Swiggy Instamart MCP endpoint is restricted (HTTP 403)."
            else:
                err_msg = e.read().decode("utf-8", errors="replace")
                summary = err_msg[:120].replace("\n", " ").strip()
                print(f"[Swiggy MCP] HTTP Error {e.code}: {summary}... Trip circuit breaker for 60s.")
                self._circuit_broken_until = time.time() + 60.0
                self._last_error = f"Swiggy Instamart is currently unavailable (HTTP {e.code})."
        except Exception as e:
            print(f"[Swiggy MCP] Connection error: {e}. Trip circuit breaker for 60s.")
            self._circuit_broken_until = time.time() + 60.0
            self._last_error = f"Swiggy Instamart is currently unavailable ({e})."

        return None

    # ── ADDRESS MANAGEMENT ───────────────────────────────────────────────────

    async def get_addresses(self) -> List[Dict[str, Any]]:
        """
        Fetches delivery addresses for the authenticated Swiggy user.
        Auto-sets the first or default address if no active address is selected.
        """
        if not self.is_live:
            active = self.oauth.get_active_address()
            return [active] if active else []

        res = await self.call_mcp_tool("get_addresses", {"page": 1, "pageSize": 10})
        if not res:
            active = self.oauth.get_active_address()
            return [active] if active else []

        addresses = res.get("addresses") or res.get("data", {}).get("addresses") or []
        if isinstance(res, list):
            addresses = res

        if addresses:
            active = self.oauth.get_active_address()
            if not active:
                # Pick default or first address
                default_addr = next((a for a in addresses if a.get("isDefault")), addresses[0])
                self.oauth.set_active_address(default_addr)

        return addresses

    async def get_or_resolve_address_id(self) -> Optional[str]:
        """Resolves active address ID, calling get_addresses if not yet set."""
        active_id = self.oauth.get_active_address_id()
        if active_id:
            return active_id

        addresses = await self.get_addresses()
        if addresses:
            addr = addresses[0]
            self.oauth.set_active_address(addr)
            return str(addr.get("id") or addr.get("addressId") or "")

        return None

    # ── PRODUCT NORMALIZATION & IMAGE RESOLUTION ──────────────────────────────

    def _resolve_image_url(self, raw_url: Any) -> Optional[str]:
        """
        Extracts genuine Swiggy CDN product image URL.
        Never fabricates, estimates, or synthesizes artwork.
        Returns None if no authentic image URL is present.
        Handles strings, lists, dicts, relative asset paths, and CDN hashes.
        """
        if not raw_url:
            return None

        # If raw_url is a list, inspect items in order
        if isinstance(raw_url, list):
            for item in raw_url:
                res = self._resolve_image_url(item)
                if res:
                    return res
            return None

        # If raw_url is a dict, inspect image fields
        if isinstance(raw_url, dict):
            for k in ("url", "imageUrl", "imageURL", "imageId", "image_id", "id", "path", "mediaUrl", "media_url", "assetId", "image", "images", "key", "creativeId"):
                val = raw_url.get(k)
                if val:
                    res = self._resolve_image_url(val)
                    if res:
                        return res
            return None

        if not isinstance(raw_url, str):
            return None

        url_str = raw_url.strip()
        if not url_str or url_str.lower() in ["none", "null", "undefined"]:
            return None

        # Fully qualified CDN URL or protocol-relative
        if url_str.startswith("//"):
            return f"https:{url_str}"
        if url_str.startswith("http://") or url_str.startswith("https://"):
            return url_str
        if url_str.startswith("media-assets.swiggy.com"):
            return f"https://{url_str}"

        # Swiggy media asset relative hash/path
        clean_path = url_str.lstrip("/")
        if clean_path.lower().startswith("ciw/"):
            clean_path = f"NI_CATALOG/IMAGES/{clean_path}"
        if "swiggy/image/upload" in clean_path:
            return f"https://media-assets.swiggy.com/{clean_path}"
        return f"https://media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,w_500/{clean_path}"

    def _normalize_variation(
        self,
        product: Dict[str, Any],
        variation: Dict[str, Any],
        is_demo: bool = False
    ) -> Dict[str, Any]:
        """
        Normalizes Swiggy Instamart product & variant into the unified Product model.
        """
        prod_id = str(product.get("productId") or product.get("id") or "swiggy_item")
        spin_id = str(
            variation.get("spinId")
            or variation.get("skuId")
            or variation.get("id")
            or f"{prod_id}_v1"
        )
        pack_size = (
            variation.get("quantityDescription")
            or variation.get("attributeValue")
            or variation.get("packSize")
            or ""
        )

        name = (
            variation.get("displayName")
            or product.get("displayName")
            or product.get("name")
            or "Product"
        )
        brand = variation.get("brandName") or product.get("brand") or None

        # Price parsing
        price_obj = variation.get("price") or {}
        if isinstance(price_obj, (int, float)):
            net_price = float(price_obj)
            mrp = float(price_obj)
        else:
            net_price = float(
                price_obj.get("offerPrice")
                or price_obj.get("netPrice")
                or price_obj.get("price")
                or 0.0
            )
            mrp = float(price_obj.get("mrp") or net_price)

        discount_amount = max(0.0, mrp - net_price)

        # Availability
        if "isInStockAndAvailable" in variation:
            is_available = bool(variation["isInStockAndAvailable"])
        elif "inStock" in variation:
            is_available = bool(variation["inStock"])
        elif "inStock" in product:
            is_available = bool(product["inStock"])
        else:
            avail_obj = variation.get("availability") or {}
            is_available = (
                avail_obj if isinstance(avail_obj, bool)
                else bool(avail_obj.get("inStock", True))
            )

        # ── Image URL resolution (Priority 1: Swiggy CDN) ─────────────────────
        # Inspect ALL known field names that the Swiggy MCP may use for images.
        # ONLY use a field if it is actually present in the response - never fabricate.
        raw_img_candidates = [
            variation.get("image"),
            variation.get("images"),
            variation.get("imageUrl"),
            variation.get("imageURL"),
            variation.get("image_url"),
            variation.get("imageId"),
            variation.get("image_id"),
            variation.get("imageIds"),
            variation.get("cloudinaryImageId"),
            variation.get("thumbnail"),
            variation.get("thumbnailUrl"),
            variation.get("thumbnail_url"),
            variation.get("media"),
            variation.get("mediaUrl"),
            variation.get("media_url"),
            variation.get("assets"),
            variation.get("productImages"),
            variation.get("spinImage"),
            product.get("image"),
            product.get("images"),
            product.get("imageUrl"),
            product.get("imageURL"),
            product.get("image_url"),
            product.get("imageId"),
            product.get("image_id"),
            product.get("imageIds"),
            product.get("cloudinaryImageId"),
            product.get("thumbnail"),
            product.get("thumbnailUrl"),
            product.get("media"),
            product.get("mediaUrl"),
            product.get("media_url"),
            product.get("assets"),
            product.get("productImages"),
        ]
        image_url = None
        for cand in raw_img_candidates:
            if cand:
                resolved = self._resolve_image_url(cand)
                if resolved:
                    image_url = resolved
                    break

        # ── Barcode fields (may be present in real Swiggy response) ──────────
        # Used by ImageResolver Priority 2 for exact Open Food Facts lookup.
        barcode = (
            variation.get("barcode")
            or variation.get("gtin")
            or variation.get("ean")
            or variation.get("upc")
            or variation.get("ean13")
            or variation.get("gtinUpc")
            or product.get("barcode")
            or product.get("gtin")
            or product.get("ean")
            or product.get("upc")
            or None
        )

        # Parse quantity and unit from pack_size string
        quantity = None
        unit = None
        if pack_size:
            parts = pack_size.split(None, 1)
            if len(parts) == 2:
                quantity, unit = parts[0], parts[1]
            else:
                unit = pack_size

        # Category inference & tags via deterministic taxonomy
        cls_info = classify_product(name, brand, product.get("category"))
        cat_name = cls_info["category"]
        sub_name = cls_info["subcategory"]
        sec_name = cls_info["section"]
        tags = cls_info["keywords"]

        normalized = {
            "id": spin_id,
            "productId": prod_id,
            "variantId": spin_id,
            "name": name,
            "brand": brand,
            "price": net_price,
            "mrp": mrp if mrp > 0 else None,
            "discount": discount_amount,
            "quantity": quantity,
            "unit": unit,
            "pack_size": pack_size,
            # imageUrl starts as the raw Swiggy CDN value (may be None).
            # ImageResolver will enrich this asynchronously after search.
            "imageUrl": image_url,
            "image": image_url,
            "imageSource": "swiggy" if image_url else None,
            "imageConfidence": 1.0 if image_url else None,
            "imageStatus": "found" if image_url else "pending",
            # Barcode forwarded to ImageResolver for OFF Priority 2 lookup
            "barcode": str(barcode) if barcode else None,
            "availability": is_available,
            "in_stock": is_available,
            "retailer": "swiggy_instamart" if not is_demo else "demo_catalog",
            "retailerName": "Swiggy Instamart" if not is_demo else "NOVA Demo Catalog (Simulated)",
            "category": cat_name,
            "subcategory": sub_name,
            "section": sec_name,
            "tags": tags,
            "is_demo": is_demo,
            "rawData": {
                "product": product,
                "variation": variation
            }
        }

        return normalized

    # ── COMMERCE OPERATIONS ───────────────────────────────────────────────────

    async def _search_mcp_single_query(self, query_str: str) -> List[Dict[str, Any]]:
        """Helper to search live products for a single query string via Swiggy Instamart MCP."""
        address_id = await self.get_or_resolve_address_id()
        if not address_id:
            address_id = "default_address"

        args = {
            "addressId": address_id,
            "query": query_str,
            "offset": 0
        }
        res = await self.call_mcp_tool("search_products", args)
        if not res:
            return []

        raw_products = res.get("products") or res.get("data", {}).get("products") or []
        if not raw_products and isinstance(res, list):
            raw_products = res

        results = []
        for prod in raw_products:
            variations = prod.get("variations") or [{}]
            for var in variations:
                results.append(self._normalize_variation(prod, var, is_demo=False))

        if results:
            try:
                results = await image_resolver.resolve_batch(results)
            except Exception as img_err:
                print(f"[IMAGE RESOLVER] Batch resolution error (non-fatal): {img_err}")

        return results

    async def search_products(self, query: str = "", category: Optional[Any] = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Searches live products via Swiggy Instamart MCP search_products tool.
        Supports both text queries, category filtering, and pooled multi-category live catalog.
        """
        if isinstance(category, dict):
            if filters is None:
                filters = category
            category = category.get("category")

        query_str = (query or "").strip()
        cat_filter = (category or "").strip().lower() if isinstance(category, str) else None
        if not cat_filter and isinstance(filters, dict) and "category" in filters:
            raw_c = filters.get("category")
            if isinstance(raw_c, str):
                cat_filter = raw_c.strip().lower()

        if cat_filter in ["all", "all items", "none", ""]:
            cat_filter = None

        print(f"[Commerce] Searching Swiggy Instamart for query='{query_str}', category='{cat_filter}'")

        # 1. Live Commerce Search
        if self.is_live:
            if self.is_circuit_broken:
                print(f"[Commerce] Swiggy MCP circuit breaker is active. Falling back to simulated catalog.")
                return self._get_simulated_catalog(query_str, cat_filter)

            if query_str:
                try:
                    results = await asyncio.wait_for(self._search_mcp_single_query(query_str), timeout=1.8)
                except Exception as e:
                    print(f"[Commerce] Live search for '{query_str}' error/timeout ({e}). Using simulated catalog.")
                    results = []

                if cat_filter and results:
                    results = [
                        p for p in results
                        if cat_filter in p.get("category", "").lower() or any(cat_filter in t.lower() for t in p.get("tags", []))
                    ]
                if results:
                    return results
                # Fallback to local catalog if live MCP found nothing
                return self._get_simulated_catalog(query_str, cat_filter)

            elif cat_filter:
                query_map = {
                    "milk": "milk curd paneer",
                    "dairy": "milk curd paneer",
                    "noodles": "maggi noodles pasta",
                    "cleaning": "detergent cleaner soap",
                    "household": "detergent cleaner soap",
                    "oil": "sunflower cooking oil",
                    "grains": "atta basmati rice",
                    "atta": "atta whole wheat flour",
                    "rice": "basmati rice",
                    "dal": "toor dal pulses",
                    "staples": "tea coffee sugar salt",
                    "tea": "tea chai coffee",
                    "snacks": "biscuits namkeen chips",
                    "beverages": "cold drinks juice",
                }
                mapped_q = query_map.get(cat_filter, cat_filter)
                results = await self._search_mcp_single_query(mapped_q)
                return results

            else:
                now = time.time()
                if self._catalog_cache and (now - self._catalog_cache_time < 600):
                    print(f"[Commerce] Returning cached live catalog ({len(self._catalog_cache)} items)")
                    return self._catalog_cache

                core_queries = [
                    "milk", "curd", "atta", "basmati rice", "sunflower oil", "toor dal",
                    "tea", "coffee", "maggi noodles", "biscuits", "namkeen", "cold drink",
                    "surf excel detergent", "vim dishwash", "harpic cleaner"
                ]
                tasks = [self._search_mcp_single_query(q) for q in core_queries]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                combined: List[Dict[str, Any]] = []
                seen_ids = set()
                valid_lists = [res for res in batch_results if isinstance(res, list)]
                max_len = max((len(l) for l in valid_lists), default=0)
                for idx in range(max_len):
                    for res_list in valid_lists:
                        if idx < len(res_list):
                            item = res_list[idx]
                            item_id = item.get("id") or item.get("variantId")
                            if item_id and item_id not in seen_ids:
                                seen_ids.add(item_id)
                                combined.append(item)

                if combined:
                    self._catalog_cache = combined
                    self._catalog_cache_time = now
                    print(f"[Commerce] Cached {len(combined)} live Swiggy items across core categories")
                return combined

        # 2. If unauthenticated or COMMERCE_MODE == "mock", return clearly labeled simulated catalog
        print("[Commerce] Returning simulated catalog (Mock / Unauthenticated)")
        return self._get_simulated_catalog(query_str, cat_filter)

    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single product by variant or product ID."""
        # Check active carts first
        for cart_items in self.carts.values():
            for item in cart_items:
                if item.get("id") == product_id or item.get("productId") == product_id or item.get("variantId") == product_id:
                    return item

        # Check catalog cache
        if self._catalog_cache:
            for item in self._catalog_cache:
                if item.get("id") == product_id or item.get("productId") == product_id or item.get("variantId") == product_id:
                    return item

        # Check simulated catalog fallback (or when simulated product ID is passed)
        for item in self._get_simulated_catalog(""):
            if item.get("id") == product_id or item.get("productId") == product_id or item.get("variantId") == product_id:
                return item

        # Fallback to search
        items = await self.search_products("")
        for item in items:
            if item.get("id") == product_id or item.get("productId") == product_id or item.get("variantId") == product_id:
                return item
        return None

    async def check_availability(self, product_id: str) -> bool:
        p = await self.get_product(product_id)
        return bool(p and p.get("availability"))

    # ── CART OPERATIONS ───────────────────────────────────────────────────────

    async def create_cart(self) -> str:
        """Initializes cart via Swiggy MCP get_cart / local session."""
        if self.is_live:
            await self.call_mcp_tool("get_cart")
        import uuid
        cart_id = f"swiggy_cart_{uuid.uuid4().hex[:8]}"
        self.carts[cart_id] = []
        return cart_id

    def get_cart(self, cart_id: str) -> Dict[str, Any]:
        """Calculates accurate totals, counts, and items for the cart."""
        items = self.carts.get(cart_id, [])
        subtotal = round(sum(float(i.get("price", 0)) * int(i.get("quantity", 1)) for i in items), 2)
        item_count = sum(int(i.get("quantity", 1)) for i in items)
        return {
            "cart_id": cart_id,
            "items": items,
            "item_count": item_count,
            "subtotal": subtotal,
        }

    async def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        """Adds a product or increments quantity in the cart."""
        if cart_id not in self.carts:
            self.carts[cart_id] = []

        if self.is_live:
            try:
                await self.call_mcp_tool("update_cart", {
                    "items": [{"spinId": product_id, "quantity": quantity}]
                })
            except Exception as e:
                print(f"[Swiggy MCP] update_cart non-fatal: {e}")

        # Check if already present in cart
        existing = next(
            (i for i in self.carts[cart_id] if i.get("id") == product_id or i.get("variantId") == product_id or i.get("productId") == product_id),
            None
        )
        if existing:
            existing["quantity"] = int(existing.get("quantity", 1)) + max(1, quantity)
        else:
            p = await self.get_product(product_id)
            if p:
                p_copy = dict(p)
                p_copy["quantity"] = max(1, quantity)
                p_copy["product_id"] = p_copy.get("id")
                self.carts[cart_id].append(p_copy)

        return self.get_cart(cart_id)

    async def update_cart_quantity(self, cart_id: str, product_id: str, quantity: int) -> Dict[str, Any]:
        """Sets an exact quantity or removes if quantity <= 0."""
        if cart_id not in self.carts:
            self.carts[cart_id] = []

        if quantity <= 0:
            return await self.remove_from_cart(cart_id, product_id)

        existing = next(
            (i for i in self.carts[cart_id] if i.get("id") == product_id or i.get("variantId") == product_id or i.get("productId") == product_id),
            None
        )
        if existing:
            existing["quantity"] = quantity
            if self.is_live:
                try:
                    await self.call_mcp_tool("update_cart", {
                        "items": [{"spinId": product_id, "quantity": quantity}]
                    })
                except Exception as mcp_err:
                    logger.warning(f"[Swiggy MCP] Failed to sync item quantity update: {mcp_err}")

        return self.get_cart(cart_id)

    async def remove_from_cart(self, cart_id: str, product_id: str) -> Dict[str, Any]:
        """Removes a product completely from the cart."""
        if cart_id in self.carts:
            self.carts[cart_id] = [
                p for p in self.carts[cart_id]
                if p.get("id") != product_id and p.get("variantId") != product_id and p.get("productId") != product_id
            ]
            if self.is_live:
                try:
                    await self.call_mcp_tool("update_cart", {
                        "items": [{"spinId": product_id, "quantity": 0}]
                    })
                except Exception as mcp_err:
                    logger.warning(f"[Swiggy MCP] Failed to sync item removal: {mcp_err}")

        return self.get_cart(cart_id)

    async def checkout(self, cart_id: str) -> Dict[str, Any]:
        """Places checkout order via Swiggy MCP checkout tool."""
        import uuid
        items = self.carts.get(cart_id, [])
        order_id = f"SWIGGY_ORD_{uuid.uuid4().hex[:8].upper()}"

        mcp_res = None
        if self.is_live:
            mcp_res = await self.call_mcp_tool("checkout", {"paymentMethod": "COD"})

        order = {
            "id": order_id,
            "orderId": order_id,
            "status": "CONFIRMED",
            "retailer": "swiggy_instamart" if self.is_live else "demo_catalog",
            "retailerName": "Swiggy Instamart" if self.is_live else "NOVA Demo Catalog",
            "source": "SWIGGY_INSTAMART_MCP" if self.is_live else "SWIGGY_INSTAMART_SIMULATED",
            "items": items,
            "total": sum(float(i.get("price", 0)) * int(i.get("quantity", 1)) for i in items),
            "eta": "10-15 min",
            "message": "Order scheduled for delivery via Swiggy Instamart in 10-15 minutes." if self.is_live else "Order simulated in Demo Mode.",
            "mcp_response": mcp_res
        }
        self.orders[order_id] = order
        return order

    def get_orders(self) -> List[Dict[str, Any]]:
        return list(self.orders.values())

    async def compare_options(self, product_id: str) -> List[Dict[str, Any]]:
        p = await self.get_product(product_id)
        if not p:
            return []

        base_price = p.get("price", 100.0)
        pack_size = p.get("pack_size", "1 unit")

        providers = [
            {"id": "swiggy", "name": "Swiggy Instamart", "eta": "10-15 min", "deliveryFee": 15},
            {"id": "blinkit", "name": "Blinkit", "eta": "12-18 min", "deliveryFee": 16},
            {"id": "zepto", "name": "Zepto", "eta": "10-15 min", "deliveryFee": 20},
            {"id": "amazon_fresh", "name": "Amazon Fresh", "eta": "Today by 6 PM", "deliveryFee": 0},
            {"id": "bigbasket", "name": "BigBasket", "eta": "Tomorrow", "deliveryFee": 0}
        ]

        offers = []
        for prov in providers:
            if prov["id"] == "swiggy":
                price = base_price
                disc = (p.get("mrp") - base_price) if p.get("mrp") and p["mrp"] > base_price else 0
            else:
                price = round(base_price * 1.02)
                disc = 0

            deliv = prov["deliveryFee"]
            eff = price + deliv
            offers.append({
                "retailerId": prov["id"],
                "retailerName": prov["name"],
                "integrationType": "Live MCP" if (prov["id"] == "swiggy" and self.is_live) else "Simulated",
                "productId": product_id,
                "productName": p.get("name"),
                "brand": p.get("brand"),
                "packSize": pack_size,
                "productPrice": price,
                "discount": disc,
                "deliveryFee": deliv,
                "serviceFee": 5,
                "effectiveTotal": eff + 5,
                "unitPrice": eff + 5,
                "availability": "IN_STOCK",
                "deliveryEstimate": prov["eta"]
            })
        return offers

    # ── ISOLATED SIMULATED CATALOG (products.json) ─────────────────────────────

    def _get_simulated_catalog(self, query: str = "", category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Loads the rich catalog from products.json (64 products) with is_demo=True.
        All products are clearly marked as demo/simulated.
        """
        import json
        catalog_file = os.path.join(os.path.dirname(__file__), "..", "catalog", "products.json")
        items = []
        if os.path.exists(catalog_file):
            try:
                with open(catalog_file, "r", encoding="utf-8") as f:
                    raw_items = json.load(f)
                for item in raw_items:
                    cls_info = classify_product(item.get("name", ""), item.get("brand", ""), item.get("category", ""))
                    cat_name = cls_info["category"]
                    sub_name = cls_info["subcategory"]
                    sec_name = cls_info["section"]
                    tags = cls_info["keywords"]
                    prod_id = item.get("id")
                    raw_img = (
                        item.get("imageUrl")
                        or item.get("image")
                        or item.get("images")
                        or item.get("imageId")
                    )
                    if raw_img and str(raw_img).startswith("/assets/fallbacks/"):
                        raw_img = None
                    resolved_img = self._resolve_image_url(raw_img) if raw_img else None
                    if resolved_img:
                        img = resolved_img
                        img_status = "found"
                        img_source = "catalog"
                    else:
                        img = None
                        img_status = "pending"
                        img_source = None

                    items.append({
                        "id": prod_id,
                        "productId": prod_id,
                        "variantId": prod_id,
                        "name": item.get("name", ""),
                        "brand": item.get("brand", ""),
                        "price": float(item.get("price", 0)),
                        "mrp": float(item["mrp"]) if item.get("mrp") else None,
                        "discount": max(0.0, float(item["mrp"]) - float(item["price"])) if item.get("mrp") else 0.0,
                        "quantity": item.get("pack_size"),
                        "unit": item.get("unit"),
                        "pack_size": item.get("pack_size"),
                        "imageUrl": img,
                        "image": img,
                        "imageSource": img_source,
                        "imageConfidence": 1.0 if img else 0.0,
                        "imageStatus": img_status,
                        "barcode": item.get("barcode"),
                        "availability": True,
                        "in_stock": True,
                        "retailer": "demo_catalog",
                        "retailerName": "NOVA Demo Catalog (Simulated)",
                        "category": cat_name,
                        "subcategory": sub_name,
                        "section": sec_name,
                        "tags": tags,
                        "is_demo": True,
                    })
            except Exception as e:
                print(f"[Simulated Catalog] Error loading products.json: {e}")

        # Filter by query & category
        q = (query or "").lower().strip()
        clean_q = re.sub(r'[^\w\s]', ' ', q).strip()
        cat = (category or "").lower().strip()
        if cat in ["all", "all items", "none"]:
            cat = ""

        # Normalize units (e.g. '1l' -> '1 l', '5kg' -> '5 kg')
        normalized_q = clean_q.replace("1l", "1 l").replace("2l", "2 l").replace("5l", "5 l").replace("1kg", "1 kg").replace("5kg", "5 kg")
        words = [w for w in normalized_q.split() if len(w) > 1]
        if not words and normalized_q:
            words = normalized_q.split()

        scored = []
        for item in items:
            name = item["name"].lower()
            brand = (item.get("brand") or "").lower()
            c = item.get("category", "").lower()
            sub = (item.get("subcategory") or "").lower()
            tags_str = " ".join(item.get("tags", [])).lower()
            full_text = f"{name} {brand} {c} {sub} {tags_str}"

            # Category filter
            if cat:
                cat_words = [w for w in cat.replace("&", " ").split() if len(w) > 2]
                cat_matches = (cat in c or cat in sub or cat in tags_str or cat in name) or any(w in c or w in sub or w in tags_str or w in name for w in cat_words)
                if not cat_matches:
                    continue

            if not q and not clean_q:
                scored.append((1, item))
                continue

            score = 0
            if q == name or clean_q == name:
                score += 200
            elif q in name or (clean_q and clean_q in name):
                score += 100
            elif q in full_text or (clean_q and clean_q in full_text):
                score += 60

            name_words = set(re.findall(r'\w+', name))
            full_words = set(re.findall(r'\w+', full_text))

            # Token-based match
            if words and all(w in name_words for w in words):
                score += 90
            elif words and all(w in full_words for w in words):
                score += 50

            for w in words:
                if w in name_words:
                    score += 40
                elif any(nw.startswith(w) for nw in name_words if len(w) >= 3):
                    score += 20
                elif w in brand:
                    score += 15
                elif w in c or w in sub:
                    score += 10
                elif w in tags_str:
                    score += 5

            # Guard: If query is food/grocery and item is Personal Care or Household, penalize unless asked
            personal_terms = {"toothpaste", "brush", "soap", "shampoo", "conditioner", "lotion", "perfume", "deodorant", "hair", "skin", "facewash"}
            if not any(pt in words for pt in personal_terms) and c in ["personal care", "beauty", "cosmetics"]:
                score -= 60

            if score > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored]
