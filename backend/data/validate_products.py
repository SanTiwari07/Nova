import json
import os

def validate_products():
    catalog_path = os.path.join(os.path.dirname(__file__), "catalog.json")
    if not os.path.exists(catalog_path):
        print("Catalog not found. Run seed_products.py first.")
        return
        
    with open(catalog_path, "r") as f:
        products = json.load(f)
        
    print(f"Validating {len(products)} products...")
    
    ids = set()
    skus = set()
    
    errors = 0
    
    for p in products:
        # Check required fields
        for field in ["id", "sku", "name", "brand", "category", "image", "price", "pack_size", "provider"]:
            if field not in p:
                print(f"Error: Product {p.get('id', 'UNKNOWN')} missing field {field}")
                errors += 1
                
        # Check uniqueness
        if p["id"] in ids:
            print(f"Error: Duplicate ID {p['id']}")
            errors += 1
        ids.add(p["id"])
        
        if p["sku"] in skus:
            print(f"Error: Duplicate SKU {p['sku']}")
            errors += 1
        skus.add(p["sku"])
        
        # Check price validity
        if not isinstance(p["price"], (int, float)) or p["price"] <= 0:
            print(f"Error: Invalid price for {p['id']}")
            errors += 1
            
        # Optional: Check image path starts with /products/
        if not str(p["image"]).startswith("/products/"):
            print(f"Error: Invalid image path for {p['id']}")
            errors += 1

    if errors == 0:
        print("Validation passed. 0 errors.")
    else:
        print(f"Validation failed with {errors} errors.")

if __name__ == "__main__":
    validate_products()
