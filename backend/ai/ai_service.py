from typing import Dict, Any, List
from .gemini_provider import GeminiProvider
from .fallback_provider import FallbackProvider

class AIService:
    def __init__(self):
        self.gemini = GeminiProvider()
        self.fallback = FallbackProvider()

    async def understand_intent(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return await self.gemini.understand_intent(user_request, context)
        except Exception as e:
            print(f"Falling back due to: {e}")
            return await self.fallback.understand_intent(user_request, context)

    async def generate_response(self, user_request: str, decision: str, evidence: Dict[str, Any]) -> str:
        try:
            return await self.gemini.generate_response(user_request, decision, evidence)
        except Exception as e:
            print(f"Falling back due to: {e}")
            return await self.fallback.generate_response(user_request, decision, evidence)

    async def generate_requirements(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            return await self.gemini.generate_requirements(intent)
        except Exception as e:
            print(f"Falling back due to: {e}")
            return await self.fallback.generate_requirements(intent)
