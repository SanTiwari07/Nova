import urllib.request
import json

req_body = json.dumps({
    "product_key": "swiggy:spin_maggi_4pk",
    "name": "MAGGI 2-Minute Instant Noodles, Made With Quality Spices",
    "brand": "Maggi",
    "quantity": "280",
    "unit": "g",
    "pack_size": "280 g",
    "barcode": None,
    "swiggy_image_url": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"
}).encode("utf-8")

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/images/resolve",
    data=req_body,
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        print(f"Status: {resp.status}")
        print("Response:", resp.read().decode("utf-8"))
except Exception as e:
    print(f"Failed: {e}")
