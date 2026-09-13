"""
Quick test: POST to /api/images/resolve and print the result.
Uses a 90s timeout since OFF may be slow.
"""
import urllib.request
import json

base = "http://127.0.0.1:8000"

# First clear all unavailable entries
req = urllib.request.Request(
    f"{base}/api/images/cache/clear-unavailable",
    data=b"{}",
    method="POST",
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req, timeout=5) as r:
    print("Cache cleared:", json.loads(r.read()))
print()

# Test Maggi (most popular, most likely to be in OFF)
payload = json.dumps({
    "product_key": "demo_catalog:prod_000140",
    "name": "Maggi 2-Minute Masala Noodles 70 g",
    "brand": "Maggi",
    "pack_size": "70 g",
    "quantity": "70",
    "unit": "g",
    "barcode": None,
    "swiggy_image_url": None,
}).encode("utf-8")

print("Calling /api/images/resolve for Maggi 70g (timeout=90s)...")
try:
    req = urllib.request.Request(
        f"{base}/api/images/resolve",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        result = json.loads(r.read())
    print("Result:", json.dumps(result, indent=2))
except Exception as e:
    print(f"ERROR: {e}")
