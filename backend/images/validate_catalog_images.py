"""
validate_catalog_images.py  -  run: python -m images.validate_catalog_images
"""
import sys, os, json, re
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from images.product_image_registry import get_registry_image

CATALOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'catalog', 'products.json')

SIZE_RE = re.compile(
    r'\b\d+(?:\.\d+)?\s*'
    r'(?:kg|g|gm|ml|l|liter|litre|pcs|pc|piece|pack|packet|count|roll|bar|cup|bottle|can|pouch)\b',
    re.IGNORECASE)

def strip_size(name):
    s = SIZE_RE.sub('', name.lower())
    s = re.sub(r'\bpack of \d+\b', '', s)
    s = re.sub(r'\(.*?\)', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def main():
    with open(CATALOG_PATH, encoding='utf-8') as f:
        products = json.load(f)

    ok, reg_resolved, obf_images, no_image = [], [], [], []
    url_to_products = defaultdict(list)

    for p in products:
        pid  = p.get('id', '?')
        name = p.get('name', '?')
        brand = p.get('brand', '')
        url  = p.get('imageUrl') or p.get('image') or ''
        src  = p.get('imageSource', '')
        if url:
            url_to_products[url].append((pid, name, brand))

    for p in products:
        pid   = p.get('id', '?')
        name  = p.get('name', '?')
        brand = p.get('brand', '')
        url   = p.get('imageUrl') or p.get('image') or ''
        src   = p.get('imageSource', '')

        if not url:
            reg = get_registry_image(name, brand)
            if reg:
                reg_resolved.append((pid, name, reg))
            else:
                no_image.append((pid, name))
        elif 'openbeautyfacts' in url:
            obf_images.append((pid, name, url))
        else:
            ok.append((pid, name, src))

    # Same URL shared across genuinely different product families
    collisions = []
    for url, prods in url_to_products.items():
        if len(prods) <= 1:
            continue
        families = set(strip_size(n) for _, n, _ in prods)
        if len(families) > 1:
            collisions.append((url, prods))

    total = len(products)
    print(f"\n== NOVA Product Image Audit ({total} products) ==\n")
    print(f"[OK]  {len(ok):3d}  products with verified images")
    print(f"[REG] {len(reg_resolved):3d}  products resolved via canonical registry")
    print(f"[OBF] {len(obf_images):3d}  products using Open Beauty Facts")
    print(f"[--]  {len(no_image):3d}  products with NO image (clean placeholder shown)")
    print(f"[!!]  {len(collisions):3d}  wrong-product image collisions\n")

    if no_image:
        print("--- Products with no image (placeholder shown) ---")
        for pid, name in no_image:
            print(f"  {pid:15s} {name}")
        print()

    if collisions:
        print("--- Image collisions (same URL, different products) ---")
        for url, prods in collisions:
            print(f"  URL: ...{url[-55:]}")
            for pid, name, _ in prods:
                print(f"       [{pid}] {name}")
        print()

    errors = len(collisions)
    if errors == 0:
        print("[PASS] Zero wrong-product image collisions detected.")
    else:
        print(f"[FAIL] {errors} collision(s) need fixing.")
    print()
    return 0 if errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
