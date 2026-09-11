import json
import os

def build_index():
    catalog_path = os.path.join(os.path.dirname(__file__), "catalog.json")
    if not os.path.exists(catalog_path):
        print("Catalog not found. Run seed_products.py first.")
        return
        
    with open(catalog_path, "r") as f:
        products = json.load(f)
        
    index = {
        "by_id": {},
        "by_category": {},
        "by_brand": {}
    }
    
    for p in products:
        index["by_id"][p["id"]] = p
        
        cat = p["category"]
        if cat not in index["by_category"]:
            index["by_category"][cat] = []
        index["by_category"][cat].append(p["id"])
        
        brand = p["brand"]
        if brand not in index["by_brand"]:
            index["by_brand"][brand] = []
        index["by_brand"][brand].append(p["id"])
        
    out_path = os.path.join(os.path.dirname(__file__), "catalog_index.json")
    with open(out_path, "w") as f:
        json.dump(index, f, indent=2)
        
    print(f"Index built successfully in {out_path}")

if __name__ == "__main__":
    build_index()
