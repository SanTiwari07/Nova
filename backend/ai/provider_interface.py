from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    
    @abstractmethod
    async def understand_intent(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Convert natural language to structured intent."""
        pass
        
    @abstractmethod
    async def generate_response(self, user_request: str, decision: str, evidence: Dict[str, Any]) -> str:
        """Generate a natural language explanation of a decision."""
        pass
        
    @abstractmethod
    async def generate_requirements(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Determine product requirements from an intent."""
        pass
