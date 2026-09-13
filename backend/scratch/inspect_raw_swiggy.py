import os
import sys
import json
import asyncio

# Ensure backend root is on pythonpath
sys.path.insert(0, os.path.abspath("backend"))

from commerce.swiggy_adapter import SwiggyInstamartAdapter

async def inspect():
    adapter = SwiggyInstamartAdapter()
    print(f"Is authenticated: {adapter.is_authenticated()}")
    print(f"Is live: {adapter.is_live}")
    token = adapter.oauth.get_access_token()
    print(f"Token present: {bool(token)}")
    address_id = await adapter.get_or_resolve_address_id()
    print(f"Address ID: {address_id}")

    test_queries = [
        "Fortune Sunflower Oil 1 L",
        "Saffola Gold Pro Healthy Lifestyle Oil 1 L",
        "Maggi",
        "Amul Milk"
    ]

    for q in test_queries:
        print(f"\n{'='*60}\nRAW MCP CALL FOR QUERY: {q}\n{'='*60}")
        raw_res = await adapter.call_mcp_tool("search_products", {
            "addressId": address_id,
            "query": q,
            "offset": 0
        })
        if not raw_res:
            print(f"No response from MCP for '{q}'. Last error: {adapter.last_error}")
            continue

        # Print top-level keys
        print(f"Response type: {type(raw_res)}")
        if isinstance(raw_res, dict):
            print(f"Keys in response: {list(raw_res.keys())}")
            # If products or data
            prods = raw_res.get("products") or raw_res.get("data", {}).get("products") or []
            print(f"Number of raw products: {len(prods)}")
            if prods:
                print("\n--- FIRST RAW PRODUCT FULL JSON ---")
                print(json.dumps(prods[0], indent=2))
        else:
            print(f"Raw response preview: {str(raw_res)[:500]}")

if __name__ == "__main__":
    asyncio.run(inspect())
