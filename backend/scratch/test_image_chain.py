import urllib.request
import json

base = "http://127.0.0.1:8000"

test_products = [
    {
        "product_key": "demo_catalog:prod_000031",
        "name": "Fortune Sunflower Oil 1 L",
        "brand": "Fortune",
        "pack_size": "1 L",
        "quantity": "1",
        "unit": "L",
        "barcode": None
    },
    {
        "product_key": "demo_catalog:prod_000032",
        "name": "Saffola Gold Pro Healthy Lifestyle Oil 1 L",
        "brand": "Saffola",
        "pack_size": "1 L",
        "quantity": "1",
        "unit": "L",
        "barcode": None
    },
    {
        "product_key": "demo_catalog:prod_000051",
        "name": "Tata Salt Lite Low Sodium 1 kg",
        "brand": "Tata Salt",
        "pack_size": "1 kg",
        "quantity": "1",
        "unit": "kg",
        "barcode": None
    },
    {
        "product_key": "demo_catalog:prod_000140",
        "name": "Maggi 2-Minute Masala Noodles 70 g",
        "brand": "Maggi",
        "pack_size": "70 g",
        "quantity": "70",
        "unit": "g",
        "barcode": None
    },
]

print("Testing /api/images/resolve for each product...")
print()

for tp in test_products:
    product_name = tp["name"]
    try:
        payload = json.dumps(tp).encode("utf-8")
        req = urllib.request.Request(
            f"{base}/api/images/resolve",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
        print(f"Product: {product_name}")
        print(f"  imageUrl: {result.get('imageUrl')}")
        print(f"  source: {result.get('imageSource')}")
        print(f"  status: {result.get('imageStatus')}")
        print()
    except Exception as e:
        print(f"ERROR for {product_name}: {e}")
        print()
