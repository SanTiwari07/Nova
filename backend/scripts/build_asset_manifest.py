import json
import os

def build_manifest():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    catalog_path = os.path.join(base_dir, "catalog", "products.json")
    manifest_path = os.path.join(base_dir, "catalog", "asset_manifest.json")
    
    if not os.path.exists(catalog_path):
        print("Products catalog not found. Run generate_catalog.py first.")
        return
        
    with open(catalog_path, 'r') as f:
        products = json.load(f)
        
    manifest = {}
    for p in products:
        product_id = p["id"]
        image = p["image"]
        
        manifest[product_id] = {
            "thumbnail": image,
            "medium": image,
            "status": p.get("asset_status", "unverified"),
            "product_id": product_id,
            "category": p.get("category", "").lower(),
            "brand": p.get("brand", "")
        }
        
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Asset manifest generated with {len(manifest)} entries at {manifest_path}")

if __name__ == "__main__":
    build_manifest()
