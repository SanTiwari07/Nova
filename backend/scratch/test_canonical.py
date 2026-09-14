from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.main import app

client = TestClient(app)

tests = [
    "Surf Excel Matic Front Load Detergent Powder 2 kg",
    "Surf Excel Matic Front Load Detergent Powder 5 kg",
    "Surf Excel Easy Wash Detergent Powder 1 kg",
    "Surf Excel Easy Wash Detergent Powder 5 kg",
    "Ariel Matic Front Load Detergent 2 kg",
    "Vim Dishwash Liquid Gel Lemon 500 ml",
    "Vim Dishwash Liquid Gel Lemon 750 ml",
    "Lizol Disinfectant Floor Cleaner Citrus 1 L",
    "Harpic Power Plus Original 1 L"
]

print("Testing Canonical Mapper")
for name in tests:
    res = client.post("/api/images/resolve", json={
        "product_key": "test_key",
        "name": name,
        "brand": name.split()[0] + " " + name.split()[1] if "Surf" in name else name.split()[0]
    })
    data = res.json()
    print(f"\nProduct: {name}")
    print(f"  URL: {data.get('imageUrl')}")
    print(f"  Source: {data.get('imageSource')}")
