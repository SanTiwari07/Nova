import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.abspath("backend"))

from commerce.swiggy_adapter import SwiggyInstamartAdapter
from images.image_resolver import ImageResolver
from images.image_cache import image_cache

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

async def test_products():
    adapter = SwiggyInstamartAdapter()
    resolver = ImageResolver()

    print(f"COMMERCE MODE: {adapter.commerce_mode}, is_live: {adapter.is_live}")
    
    for q in test_queries:
        print(f"\n{'='*70}\nTEST PRODUCT SEARCH: {q}\n{'='*70}")
        products = await adapter.search_products(query=q)
        if not products:
            print(f"NO PRODUCTS FOUND FOR QUERY: {q}")
            continue

        print(f"Found {len(products)} products. Inspecting top 3:")
        for idx, p in enumerate(products[:3]):
            print(f"\n--- Result #{idx+1} ---")
            print(f"Name: {p.get('name')}")
            print(f"Brand: {p.get('brand')}")
            print(f"ID: {p.get('id')}")
            print(f"Variant ID: {p.get('variantId')}")
            print(f"Price: {p.get('price')}")
            print(f"Pack Size: {p.get('pack_size')}")
            print(f"Barcode: {p.get('barcode')}")
            print(f"Swiggy Image: {p.get('imageUrl')}")
            print(f"Image Source: {p.get('imageSource')}")
            print(f"Image Status: {p.get('imageStatus')}")

if __name__ == "__main__":
    asyncio.run(test_products())
