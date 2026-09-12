import os
import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from .interface import CommerceInterface
from .swiggy_oauth import oauth_manager

SWIGGY_MCP_URL = os.environ.get("SWIGGY_MCP_URL", "https://mcp.swiggy.com/im")
COMMERCE_MODE = os.environ.get("COMMERCE_MODE", "live").lower()

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

    @property
    def is_live(self) -> bool:
        """True if authenticated with a valid Swiggy OAuth access token."""
        return self.oauth.is_authenticated()

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
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "Household-Autopilot/1.0"
        }

        req = urllib.request.Request(self.mcp_url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                status_code = response.status
                print(f"[Commerce] Swiggy MCP response status: {status_code}")
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

                # Check for JSON-RPC error
                if "error" in res_json:
                    err = res_json["error"]
                    print(f"[Swiggy MCP] JSON-RPC Error: {err}")
                    return None

                # Extract tool call payload from MCP result
                result = res_json.get("result", {})
                
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
                print("[Swiggy MCP] 401 Unauthorized - token expired or revoked. Clearing session.")
                self.oauth.clear_session()
            else:
                err_msg = e.read().decode("utf-8", errors="replace")
                print(f"[Swiggy MCP] HTTP Error {e.code}: {err_msg}")
        except Exception as e:
            print(f"[Swiggy MCP] Connection error: {e}")

        return None

    # ── ADDRESS MANAGEMENT ───────────────────────────────────────────────────

    async def get_addresses(self) -> List[Dict[str, Any]]:
        """
        Fetches delivery addresses for the authenticated Swiggy user.
        Auto-sets the first or default address if no active address is selected.
        """
        if not self.is_live:
            return []

        res = await self.call_mcp_tool("get_addresses", {"page": 1, "pageSize": 10})
        if not res:
            return []

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
        """
        if isinstance(raw_url, list) and raw_url:
            raw_url = raw_url[0]

        if not raw_url or not isinstance(raw_url, str):
            return None

        url_str = raw_url.strip()
        if not url_str or url_str.lower() in ["none", "null", "undefined"]:
            return None

        # Fully qualified CDN URL
        if url_str.startswith("http://") or url_str.startswith("https://"):
            return url_str

        # Swiggy media asset relative hash/path
        # Format: media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,w_500/<hash>
        clean_path = url_str.lstrip("/")
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

        # Real commerce image URL or None - NO image generation
        raw_img = (
            variation.get("imageUrl")
            or variation.get("imageURL")
            or product.get("imageUrl")
            or product.get("imageURL")
        )
        image_url = self._resolve_image_url(raw_img)

        # Parse quantity and unit from pack_size string
        quantity = None
        unit = None
        if pack_size:
            parts = pack_size.split(None, 1)
            if len(parts) == 2:
                quantity, unit = parts[0], parts[1]
            else:
                unit = pack_size

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
            "imageUrl": image_url,
            "image": image_url,
            "availability": is_available,
            "in_stock": is_available,
            "retailer": "swiggy_instamart",
            "retailerName": "Swiggy Instamart",
            "category": product.get("category", "Grocery"),
            "is_demo": is_demo,
            "rawData": {
                "product": product,
                "variation": variation
            }
        }

        # User requirement structured log
        print(
            f"[Product Adapter] Product ID: {normalized['productId']} "
            f"Variant ID: {normalized['variantId']} "
            f"Name: {normalized['name']} "
            f"Price: Rs. {normalized['price']} "
            f"MRP: Rs. {normalized['mrp']} "
            f"Image URL: {normalized['imageUrl']} "
            f"Image source: SWIGGY INSTAMART"
        )

        return normalized

    # ── COMMERCE OPERATIONS ───────────────────────────────────────────────────

    async def search_products(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Searches live products via Swiggy Instamart MCP search_products tool.
        """
        query_str = (query or "").strip()
        print(f"[Commerce] Searching Swiggy Instamart for: {query_str}")

        # 1. Live MCP Search
        if self.is_live:
            address_id = await self.get_or_resolve_address_id()
            if not address_id:
                print("[Swiggy MCP] Warning: No active address selected for Swiggy search.")
                address_id = "default_address"

            args = {
                "addressId": address_id,
                "query": query_str or "groceries",
                "offset": 0
            }
            res = await self.call_mcp_tool("search_products", args)
            if res:
                raw_products = res.get("products") or res.get("data", {}).get("products") or []
                if not raw_products and isinstance(res, list):
                    raw_products = res

                print(f"[Commerce] Found {len(raw_products)} products")

                if raw_products:
                    # Log first product raw JSON for verification during development
                    try:
                        print(f"[Swiggy MCP] Sample raw product schema:\n{json.dumps(raw_products[0], indent=2)[:500]}")
                    except Exception:
                        pass

                    results = []
                    for prod in raw_products:
                        variations = prod.get("variations") or [{}]
                        for var in variations:
                            results.append(self._normalize_variation(prod, var, is_demo=False))
                    if results:
                        return results

        # 2. If unauthenticated and COMMERCE_MODE == "mock", return clearly labeled simulated catalog
        if COMMERCE_MODE == "mock":
            print("[Commerce] Running in COMMERCE_MODE=mock. Using isolated simulated items.")
            return self._get_simulated_catalog(query_str)

        # 3. Default: Not connected
        print("[Commerce] Swiggy Instamart is currently not connected or returned no live items.")
        return []

    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single product by variant or product ID."""
        # Search live or mock items
        items = await self.search_products("")
        for item in items:
            if item.get("id") == product_id or item.get("productId") == product_id or item.get("variantId") == product_id:
                return item
        return None

    async def check_availability(self, product_id: str) -> bool:
        p = await self.get_product(product_id)
        return bool(p and p.get("availability"))

    async def create_cart(self) -> str:
        """Initializes cart via Swiggy MCP get_cart / local session."""
        if self.is_live:
            await self.call_mcp_tool("get_cart")
        import uuid
        cart_id = f"swiggy_cart_{uuid.uuid4().hex[:8]}"
        self.carts[cart_id] = []
        return cart_id

    async def add_to_cart(self, cart_id: str, product_id: str, quantity: int = 1):
        if cart_id not in self.carts:
            self.carts[cart_id] = []

        if self.is_live:
            await self.call_mcp_tool("update_cart", {
                "items": [{"spinId": product_id, "quantity": quantity}]
            })

        p = await self.get_product(product_id)
        if p:
            self.carts[cart_id].append(p)

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
            "retailer": "swiggy_instamart",
            "retailerName": "Swiggy Instamart",
            "source": "SWIGGY_INSTAMART_MCP" if self.is_live else "SWIGGY_INSTAMART_SIMULATED",
            "items": items,
            "total": sum(i.get("price", 0) for i in items),
            "eta": "10-15 min",
            "message": "Order scheduled for delivery via Swiggy Instamart in 10-15 minutes.",
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

    # ── ISOLATED SIMULATED CATALOG (COMMERCE_MODE=mock ONLY) ──────────────────

    def _get_simulated_catalog(self, query: str) -> List[Dict[str, Any]]:
        """
        Isolated simulated catalog strictly for COMMERCE_MODE=mock.
        Every product is labeled is_demo=True.
        imageUrl is None (rendered as neutral UI placeholder) — NEVER AI-generated.
        """
        catalog = [
            {
                "productId": "swiggy_maggi_masala",
                "name": "Maggi 2-Minute Masala Instant Noodles",
                "brand": "Maggi",
                "category": "Noodles",
                "variations": [
                    {
                        "spinId": "spin_maggi_4pk",
                        "attributeValue": "280 g (Pack of 4)",
                        "price": {"mrp": 60.0, "netPrice": 56.0},
                        "availability": {"inStock": True},
                        "imageUrl": None
                    },
                    {
                        "spinId": "spin_maggi_single",
                        "attributeValue": "70 g",
                        "price": {"mrp": 14.0, "netPrice": 14.0},
                        "availability": {"inStock": True},
                        "imageUrl": None
                    }
                ]
            },
            {
                "productId": "swiggy_amul_taaza",
                "name": "Amul Taaza Homogenised Toned Milk",
                "brand": "Amul",
                "category": "Milk",
                "variations": [
                    {
                        "spinId": "spin_amul_taaza_1l",
                        "attributeValue": "1 L (Tetra Pak)",
                        "price": {"mrp": 75.0, "netPrice": 72.0},
                        "availability": {"inStock": True},
                        "imageUrl": None
                    }
                ]
            },
            {
                "productId": "swiggy_india_gate_basmati",
                "name": "India Gate Basmati Rice Feast Rozzana",
                "brand": "India Gate",
                "category": "Rice",
                "variations": [
                    {
                        "spinId": "spin_indiagate_5kg",
                        "attributeValue": "5 kg",
                        "price": {"mrp": 550.0, "netPrice": 465.0},
                        "availability": {"inStock": True},
                        "imageUrl": None
                    }
                ]
            },
            {
                "productId": "swiggy_harpic_1000ml",
                "name": "Harpic Power Plus 10X Max Clean Toilet Cleaner",
                "brand": "Harpic",
                "category": "Cleaning",
                "variations": [
                    {
                        "spinId": "spin_harpic_1l",
                        "attributeValue": "1 L",
                        "price": {"mrp": 230.0, "netPrice": 207.0},
                        "availability": {"inStock": True},
                        "imageUrl": None
                    }
                ]
            }
        ]

        q = (query or "").lower().strip()
        results = []
        for prod in catalog:
            name = prod["name"].lower()
            brand = (prod.get("brand") or "").lower()
            cat = (prod.get("category") or "").lower()
            if not q or q in name or q in brand or q in cat:
                for var in prod.get("variations", []):
                    results.append(self._normalize_variation(prod, var, is_demo=True))

        return results
