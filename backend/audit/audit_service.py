from typing import List, Dict, Any
from datetime import datetime
import uuid

class AuditService:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.logs = []
        
    def log_decision(self, product_name: str, decision: str, reasons: List[str]):
        self.logs.insert(0, {
            "id": f"evt_{uuid.uuid4().hex[:8]}",
            "product": product_name,
            "decision": decision,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self.logs[:limit]
