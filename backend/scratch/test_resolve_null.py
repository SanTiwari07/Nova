import urllib.request
import json

test_cases = [
    {
        "product_key": "test_fortune_1l",
        "name": "Fortune Sunlite Refined Sunflower Oil",
        "brand": "Fortune",
        "quantity": "1",
        "unit": "L",
        "pack_size": "1 L",
        "barcode": None,
        "swiggy_image_url": None
    },
    {
        "product_key": "test_tata_tea",
        "name": "Tata Tea Premium",
        "brand": "Tata Tea",
        "quantity": "500",
        "unit": "g",
        "pack_size": "500 g",
        "barcode": None,
        "swiggy_image_url": None
    }
]

for tc in test_cases:
    print(f"\nTesting resolve for: {tc['name']}")
    req_body = json.dumps(tc).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/images/resolve",
        data=req_body,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print("Response:", resp.read().decode("utf-8"))
    except Exception as e:
        print("Failed:", e)
