import urllib.request
import json

try:
    req = urllib.request.urlopen("http://127.0.0.1:8000/api/products?limit=10")
    data = json.loads(req.read().decode("utf-8"))
    print(f"Total products returned: {len(data)}")
    for i, p in enumerate(data[:5]):
        print(f"\n[{i+1}] Name: {p.get('name')}")
        print(f"    Brand: {p.get('brand')}")
        print(f"    Price: {p.get('price')}")
        print(f"    Pack Size: {p.get('pack_size')}")
        print(f"    Image URL: {p.get('imageUrl')}")
        print(f"    Image Source: {p.get('imageSource')}")
        print(f"    Image Status: {p.get('imageStatus')}")
        print(f"    Barcode: {p.get('barcode')}")
except Exception as e:
    print(f"Error: {e}")
