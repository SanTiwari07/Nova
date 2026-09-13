import json
import os
from typing import List, Dict, Any, Optional
from .taxonomy import classify_product, CANONICAL_CATEGORIES

class ProductRepository:
    def __init__(self):
        self.catalog_path = os.path.join(os.path.dirname(__file__), "products.json")
        self.products: List[Dict[str, Any]] = []
        self._load_catalog()
        
    def _load_catalog(self):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            self.products = []
            for p in raw:
                item = dict(p)
                cls_info = classify_product(item.get("name", ""), item.get("brand", ""), item.get("category", ""))
                item["category"] = cls_info["category"]
                item["subcategory"] = cls_info["subcategory"]
                item["section"] = cls_info["section"]
                item["keywords"] = cls_info["keywords"]
                # Authenticate image URL - only genuine HTTP/HTTPS URLs are retained
                raw_img = item.get("imageUrl") or item.get("image")
                if raw_img and str(raw_img).startswith("/assets/fallbacks/"):
                    raw_img = None

                if raw_img and (str(raw_img).startswith("http://") or str(raw_img).startswith("https://")):
                    item["imageUrl"] = raw_img
                    item["image"] = raw_img
                    item["images"] = [raw_img]
                    item["imageStatus"] = "found"
                    item["imageSource"] = "catalog"
                else:
                    item["imageUrl"] = None
                    item["image"] = None
                    item["images"] = []
                    item["imageStatus"] = "unavailable"
                    item["imageSource"] = None
                self.products.append(item)
                
    def get_all(self, skip: int = 0, limit: int = 250) -> List[Dict[str, Any]]:
        return self.products[skip:skip+limit]
        
    def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        for p in self.products:
            if p.get("id") == product_id or p.get("productId") == product_id:
                return p
        return None
        
    def search(self, query: str, skip: int = 0, limit: int = 250) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        if not q:
            return self.products[skip:skip+limit]

        # 1. Exact phrase match
        exact = [
            p for p in self.products 
            if q in p.get("name", "").lower() 
            or q in (p.get("brand") or "").lower() 
            or q in p.get("category", "").lower()
            or q in (p.get("subcategory") or "").lower()
            or any(q in t.lower() for t in p.get("tags", []))
        ]
        if exact:
            return exact[skip:skip+limit]

        # 2. Tokenized search with unit normalization (e.g. '1l' -> '1 l', '5l' -> '5 l')
        normalized = q.replace("1l", "1 l").replace("2l", "2 l").replace("5l", "5 l").replace("1kg", "1 kg").replace("5kg", "5 kg")
        words = [w for w in normalized.split() if len(w) > 1]
        if not words:
            words = q.split()

        scored = []
        for p in self.products:
            text = f"{p.get('name', '')} {p.get('brand', '')} {p.get('category', '')} {' '.join(p.get('tags', []))}".lower()
            match_count = sum(1 for w in words if w in text)
            if match_count > 0:
                scored.append((match_count, p))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored][skip:skip+limit]
        
    def get_categories(self) -> List[str]:
        return list(CANONICAL_CATEGORIES.keys())

