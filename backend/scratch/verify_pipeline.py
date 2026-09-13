import sys
import os
import json
import urllib.request

sys.path.insert(0, "backend")

from commerce.swiggy_adapter import SwiggyInstamartAdapter
from images.image_validator import validate_image_url

adapter = SwiggyInstamartAdapter()

raw_products = [
    {
        "product": {"id": "prod_swiggy_maggi", "name": "Maggi 2-Minute Masala Instant Noodles", "brand": "Maggi"},
        "variation": {
            "id": "var_maggi_70g",
            "displayName": "Maggi 2-Minute Masala Instant Noodles 70 g",
            "quantityDescription": "70 g",
            "price": {"mrp": 14.0, "offerPrice": 14.0},
            "images": ["NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"],
        }
    },
    {
        "product": {"id": "prod_swiggy_oil", "name": "Fortune Sunlite Refined Sunflower Oil", "brand": "Fortune"},
        "variation": {
            "id": "var_fortune_1l",
            "displayName": "Fortune Sunlite Refined Sunflower Oil 1 L",
            "quantityDescription": "1 L",
            "price": {"mrp": 165.0, "offerPrice": 155.0},
            "imageId": "ciw/2026/2/18/d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png",
        }
    },
    {
        "product": {"id": "prod_swiggy_salt", "name": "Tata Salt Lite Low Sodium Iodised Salt", "brand": "Tata Salt"},
        "variation": {
            "id": "var_tata_salt_1kg",
            "displayName": "Tata Salt Lite Low Sodium Iodised Salt 1 kg",
            "quantityDescription": "1 kg",
            "price": {"mrp": 45.0, "offerPrice": 40.0},
            "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png",
        }
    },
    {
        "product": {"id": "prod_swiggy_milk", "name": "Amul Taaza Fresh Toned Milk", "brand": "Amul"},
        "variation": {
            "id": "var_amul_milk_1l",
            "displayName": "Amul Taaza Fresh Toned Milk 1 L",
            "quantityDescription": "1 L",
            "price": {"mrp": 75.0, "offerPrice": 72.0},
            "cloudinaryImageId": "NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png",
        }
    },
]

print("=== 1. NORMALIZATION & EXTRACTION TEST ===")
for item in raw_products:
    norm = adapter._normalize_variation(item["product"], item["variation"])
    url = norm.get("imageUrl")
    valid, reason, dims = validate_image_url(url)
    print(f"Product: {norm.get('name')}")
    print(f"  Normalized imageUrl: {url}")
    print(f"  Source: {norm.get('imageSource')}")
    print(f"  Validation: valid={valid}, dims={dims}, reason={reason}")

print("\n=== 2. API /api/images/resolve ENDPOINT TEST ===")
base = "http://127.0.0.1:8000"
for item in raw_products:
    norm = adapter._normalize_variation(item["product"], item["variation"])
    payload = json.dumps({
        "product_key": norm.get("id"),
        "name": norm.get("name"),
        "brand": norm.get("brand"),
        "quantity": norm.get("quantity"),
        "unit": norm.get("unit"),
        "pack_size": norm.get("pack_size"),
        "barcode": norm.get("barcode"),
        "swiggy_image_url": norm.get("imageUrl"),
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{base}/api/images/resolve",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print(f"Resolved {norm.get('name')}:")
        print(f"  imageUrl: {res.get('imageUrl')}")
        print(f"  imageSource: {res.get('imageSource')}")
        print(f"  imageStatus: {res.get('imageStatus')}")
