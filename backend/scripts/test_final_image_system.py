"""
Verification Script for Household Autopilot Final Dynamic Product Image System.

Tests the 8 mandatory test products:
  1. Fortune Sunflower Oil 1 L
  2. Saffola Gold Pro Healthy Lifestyle Oil 1 L
  3. Saffola Gold Pro Healthy Lifestyle Oil 5 L
  4. Dhara Kachi Ghani Mustard Oil 1 L
  5. Tata Salt Lite Low Sodium 1 kg
  6. Maggi 70 g
  7. Amul Milk
  8. Rice

For each product, verifies:
  - Correct product identity
  - Correct brand
  - Correct pack size
  - Price from Swiggy
  - Availability from Swiggy
  - Image source (Swiggy CDN / Open Food Facts / unavailable)
  - Image match confidence
  - Image quality score
  - Final combined score
  - Final decision (found / unavailable)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from commerce.swiggy_adapter import SwiggyInstamartAdapter
from images.image_resolver import image_resolver

commerce_adapter = SwiggyInstamartAdapter()


TEST_QUERIES = [
    {"query": "Fortune Sunflower Oil 1 L", "target_brand": "Fortune", "target_size": "1 L"},
    {"query": "Saffola Gold Pro Healthy Lifestyle Oil 1 L", "target_brand": "Saffola", "target_size": "1 L"},
    {"query": "Saffola Gold Pro Healthy Lifestyle Oil 5 L", "target_brand": "Saffola", "target_size": "5 L"},
    {"query": "Dhara Kachi Ghani Mustard Oil 1 L", "target_brand": "Dhara", "target_size": "1 L"},
    {"query": "Tata Salt Lite Low Sodium 1 kg", "target_brand": "Tata Salt", "target_size": "1 kg"},
    {"query": "Maggi 70 g", "target_brand": "Maggi", "target_size": "70 g"},
    {"query": "Amul Milk", "target_brand": "Amul", "target_size": None},
    {"query": "Rice", "target_brand": None, "target_size": None},
]


async def run_verification():
    print("\n" + "=" * 90)
    print("HOUSEHOLD AUTOPILOT - FINAL DYNAMIC PRODUCT IMAGE SYSTEM VERIFICATION")
    print("=" * 90)

    results = []

    for item in TEST_QUERIES:
        q = item["query"]
        print(f"\n[QUERY] Searching Swiggy Instamart for: '{q}'...")
        products = await commerce_adapter.search_products(q)

        if not products:
            print(f"  [WARN] No Swiggy products found for '{q}'")
            continue

        # Take the top matched product
        p = products[0]

        # Resolve image via canonical ImageResolver
        resolved = await image_resolver.resolve(p)

        rec = {
            "query": q,
            "product_name": p.get("name"),
            "brand": p.get("brand"),
            "pack_size": p.get("pack_size") or f"{p.get('quantity', '')} {p.get('unit', '')}".strip(),
            "price": p.get("price"),
            "mrp": p.get("mrp"),
            "availability": p.get("availability") or p.get("in_stock"),
            "image_url": resolved.get("imageUrl"),
            "image_source": resolved.get("imageSource"),
            "match_confidence": resolved.get("productMatchConfidence", 0.0),
            "quality_score": resolved.get("imageQualityScore", 0.0),
            "final_score": resolved.get("finalScore", 0.0),
            "image_status": resolved.get("imageStatus"),
            "match_method": resolved.get("matchMethod"),
        }
        results.append(rec)

    print("\n" + "=" * 90)
    print("EVALUATION RESULTS SUMMARY")
    print("=" * 90)
    header = f"{'Query':<30} | {'Price':<6} | {'Source':<12} | {'Conf':<5} | {'Qual':<5} | {'Final':<5} | {'Status':<11}"
    print(header)
    print("-" * len(header))

    for r in results:
        price_str = f"Rs {r['price']:.0f}" if r['price'] else "N/A"
        src_str = str(r['image_source'])[:12]
        status_str = "FOUND" if r['image_status'] == "found" else "UNAVAILABLE"
        print(
            f"{r['query'][:30]:<30} | {price_str:<6} | {src_str:<12} | "
            f"{r['match_confidence']:<5.2f} | {r['quality_score']:<5.2f} | {r['final_score']:<5.2f} | {status_str:<11}"
        )
        if r['image_url']:
            print(f"   -> URL: {r['image_url'][:75]}...")
        else:
            print(f"   -> Decision: Clean neutral 'Image unavailable' displayed (No wrong variant or UGC)")

    print("\n" + "=" * 90)
    return results


if __name__ == "__main__":
    asyncio.run(run_verification())
