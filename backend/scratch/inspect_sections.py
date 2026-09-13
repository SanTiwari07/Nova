import urllib.request
import json

try:
    req = urllib.request.urlopen("http://127.0.0.1:8000/api/products/sections")
    data = json.loads(req.read().decode("utf-8"))
    print(f"Sections keys: {list(data.keys())}")
    for sec, prods in data.items():
        print(f"\nSection '{sec}' has {len(prods)} products:")
        for p in prods[:2]:
            print(f"  - {p.get('name')} | price={p.get('price')} | img={p.get('imageUrl')[:60] if p.get('imageUrl') else 'None'} | src={p.get('imageSource')}")
except Exception as e:
    print(f"Error: {e}")
