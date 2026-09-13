import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.abspath("backend"))

from commerce.swiggy_adapter import SwiggyInstamartAdapter
from images.image_validator import validate_image_url

async def fetch_live_urls():
    adapter = SwiggyInstamartAdapter()
    token = adapter.oauth.get_access_token()
    print("Has token:", bool(token))
    addr = await adapter.get_or_resolve_address_id()
    print("Address:", addr)

    queries = ["Tata Tea", "Toor Dal", "Parle G Biscuits", "Coca Cola"]
    for q in queries:
        print(f"\n{'='*50}\nQuery: {q}")
        res = await adapter.call_mcp_tool("search_products", {
            "addressId": addr,
            "query": q,
            "offset": 0
        })
        if not res:
            print("No response from MCP for", q)
            continue
        prods = res.get("products") or res.get("data", {}).get("products") or []
        print(f"Found {len(prods)} products")
        for p in prods[:2]:
            name = p.get("displayName")
            for var in p.get("variations", []):
                img = var.get("imageUrl")
                valid, reason, dims = validate_image_url(img)
                print(f"  Item: {name} ({var.get('quantityDescription')})")
                print(f"  URL: {img}")
                print(f"  Valid: {valid}, reason: {reason}, dims: {dims}\n")

if __name__ == "__main__":
    asyncio.run(fetch_live_urls())
