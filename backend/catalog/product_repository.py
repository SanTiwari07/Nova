import json
import os
from typing import List, Dict, Any, Optional

class ProductRepository:
    def __init__(self):
        self.catalog_path = os.path.join(os.path.dirname(__file__), "products.json")
        self.products: List[Dict[str, Any]] = []
        self._load_catalog()
        
    def _load_catalog(self):
        if os.path.exists(self.catalog_path):
            with open(self.catalog_path, 'r') as f:
                self.products = json.load(f)
                
    def get_all(self, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        return self.products[skip:skip+limit]
        
    def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        for p in self.products:
            if p["id"] == product_id:
                return p
        return None
        
    def search(self, query: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        query = query.lower()
        results = [
            p for p in self.products 
            if query in p["name"].lower() or query in p["category"].lower() or query in p["brand"].lower()
        ]
        return results[skip:skip+limit]
        
    def get_categories(self) -> List[str]:
        cats = set(p["category"] for p in self.products if "category" in p)
        return sorted(list(cats))
