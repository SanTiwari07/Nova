import json
import os
from typing import Dict, Any, Optional

class AssetRepository:
    def __init__(self):
        self.manifest_path = os.path.join(os.path.dirname(__file__), "asset_manifest.json")
        self.manifest: Dict[str, Any] = {}
        self._load_manifest()
        
    def _load_manifest(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r') as f:
                self.manifest = json.load(f)
                
    def get_asset_for_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self.manifest.get(product_id)
        
    def get_fallback_for_category(self, category: str) -> str:
        cat_lower = category.lower() if category else ""
        return f"/assets/fallbacks/{cat_lower}.webp"
        
    def get_generic_fallback(self) -> str:
        return "/assets/fallbacks/generic.webp"
