import sys
import json
import asyncio
import urllib.request
import os

sys.path.insert(0, "backend")

from commerce.swiggy_adapter import SwiggyInstamartAdapter
from images.image_validator import validate_image_url
from images.image_resolver import ImageResolver

test_queries = [
    "Fortune Sunflower Oil 1 L",
    "Saffola Gold Pro Healthy Lifestyle Oil 1 L",
    "Saffola Gold Pro Healthy Lifestyle Oil 5 L",
    "Dhara Kachi Ghani Mustard Oil 1 L",
    "Tata Salt Lite Low Sodium 1 kg",
    "Maggi",
    "Amul Milk",
    "Rice"
]

async def run_acceptance_tests():
    adapter = SwiggyInstamartAdapter()
    resolver = ImageResolver()

    for q in test_queries:
        print("\n" + "-"*60)
        print(f"PRODUCT:\n{q}\n")

        products = await adapter.search_products(query=q)
        if not products:
            print("SWIGGY PRODUCT ID:\nNOT FOUND")
            print("SWIGGY VARIANT ID:\nNOT FOUND")
            print("BARCODE/GTIN:\nNOT FOUND")
            print("SWIGGY IMAGE:\nNOT FOUND")
            print("SWIGGY IMAGE URL:\nNone")
            print("SWIGGY IMAGE VALID:\nNO")
            print("EXTERNAL IMAGE LOOKUP:\nNO")
            print("IMAGE SOURCE:\nunavailable")
            print("IMAGE MATCH METHOD:\nnone")
            print("IMAGE URL:\nNone")
            print("IMAGE URL VALID:\nNO")
            print("IMAGE QUALITY:\nREJECTED")
            print("FINAL:\nIMAGE UNAVAILABLE")
            print("-"*60)
            continue

        # Inspect top matched product
        p = products[0]
        prod_id = p.get("productId") or p.get("id") or "N/A"
        variant_id = p.get("variantId") or p.get("id") or "N/A"
        barcode = p.get("barcode") or "NOT PROVIDED BY SWIGGY"
        
        swiggy_raw_img = p.get("rawData", {}).get("variation", {}).get("imageUrl") or p.get("imageUrl")
        swiggy_img_found = "FOUND" if swiggy_raw_img else "NOT FOUND"
        
        valid = False
        reason = "No URL"
        dims = None
        if swiggy_raw_img:
            valid, reason, dims = validate_image_url(swiggy_raw_img)

        swiggy_img_valid = "YES" if valid else "NO"
        
        external_lookup = "NO"
        image_source = p.get("imageSource") or ("swiggy" if valid else "unavailable")
        match_method = "swiggy_cdn" if valid else "none"
        final_img = p.get("imageUrl") if valid else None
        
        if not valid:
            # Test external lookup
            external_lookup = "YES"
            resolved = await resolver.resolve(p)
            final_img = resolved.get("imageUrl")
            image_source = resolved.get("imageSource", "unavailable")
            match_method = "open_food_facts" if final_img else "none"
            if final_img:
                valid, reason, dims = validate_image_url(final_img)

        final_img_valid = "YES" if (final_img and valid) else "NO"
        image_quality = "ACCEPTED" if (final_img and valid) else "REJECTED"
        final_display = "IMAGE DISPLAYED" if (final_img and valid) else "IMAGE UNAVAILABLE"

        print(f"SWIGGY PRODUCT ID:\n{prod_id}\n")
        print(f"SWIGGY VARIANT ID:\n{variant_id}\n")
        print(f"BARCODE/GTIN:\n{barcode}\n")
        print(f"SWIGGY IMAGE:\n{swiggy_img_found}\n")
        print(f"SWIGGY IMAGE URL:\n{swiggy_raw_img}\n")
        print(f"SWIGGY IMAGE VALID:\n{swiggy_img_valid}\n")
        print(f"EXTERNAL IMAGE LOOKUP:\n{external_lookup}\n")
        print(f"IMAGE SOURCE:\n{image_source}\n")
        print(f"IMAGE MATCH METHOD:\n{match_method}\n")
        print(f"IMAGE URL:\n{final_img}\n")
        print(f"IMAGE URL VALID:\n{final_img_valid}\n")
        print(f"IMAGE QUALITY:\n{image_quality}\n")
        print(f"FINAL:\n{final_display}")
        print("-"*60)

if __name__ == "__main__":
    asyncio.run(run_acceptance_tests())
