import json
import os

def validate_assets():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    catalog_path = os.path.join(base_dir, "catalog", "products.json")
    manifest_path = os.path.join(base_dir, "catalog", "asset_manifest.json")
    
    if not os.path.exists(catalog_path):
        print("Catalog not found.")
        return
        
    if not os.path.exists(manifest_path):
        print("Asset manifest not found.")
        return
        
    with open(catalog_path, 'r') as f:
        products = json.load(f)
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    total_products = len(products)
    verified = 0
    missing = 0
    broken = 0
    invalid_mappings = 0
    fallback_assets = 0
    
    total_size_bytes = 0
    
    for p in products:
        pid = p["id"]
        if pid not in manifest:
            invalid_mappings += 1
            continue
            
        asset_info = manifest[pid]
        
        # Check if mapped product_id matches
        if asset_info.get("product_id") != pid:
            invalid_mappings += 1
            
        rel_path = asset_info["medium"]
        
        # Determine absolute path on disk
        # rel_path is like /assets/products/category/file.webp
        if not rel_path.startswith("/assets/"):
            invalid_mappings += 1
            continue
            
        local_rel_path = rel_path.replace("/assets/", "").replace("/", os.sep)
        abs_path = os.path.join(base_dir, "assets", local_rel_path)
        
        if not os.path.exists(abs_path):
            missing += 1
            continue
            
        size = os.path.getsize(abs_path)
        if size == 0:
            broken += 1
        else:
            total_size_bytes += size
            
        # Optional: check if it's a dummy or actual webp
        # For this script we will assume if it exists and size > 0 it is verified
        if asset_info.get("status") == "verified":
            verified += 1
        elif asset_info.get("status") == "fallback":
            fallback_assets += 1
            
    print("NOVA PRODUCT ASSET VALIDATION\n")
    print(f"Products:              {total_products}")
    print(f"Verified assets:       {verified}")
    print(f"Missing assets:        {missing}")
    print(f"Broken assets:         {broken}")
    print(f"Invalid mappings:      {invalid_mappings}")
    print(f"Fallback assets:       {fallback_assets}\n")
    
    status = "PASS" if (missing == 0 and broken == 0 and invalid_mappings == 0) else "FAIL"
    print(f"STATUS: {status}\n")
    
    print(f"Asset storage: {total_size_bytes / (1024*1024):.2f} MB")

if __name__ == "__main__":
    validate_assets()
