import os
import json
import google.generativeai as genai
from typing import Dict, Any, List
from .provider_interface import AIProvider
from pydantic import BaseModel, Field

class IntentSchema(BaseModel):
    intent_type: str = Field(description="The type of intent, e.g. MEAL_PREPARATION, REPLENISHMENT, BUDGET_CONSTRAINT")
    confidence: float = Field(description="Confidence score between 0 and 1")
    goal: str = Field(description="The specific goal, e.g. prepare_maggi, buy_milk")
    time_context: str = Field(description="When the intent applies, e.g. tonight, this_week")
    requires_inventory_check: bool = Field(description="True if we need to check pantry")

class RequirementItem(BaseModel):
    query: str = Field(description="Generic product name like 'Maggi noodles'")
    quantity: int = Field(description="Estimated quantity needed")

class RequirementSchema(BaseModel):
    requirements: list[RequirementItem]

class GeminiProvider(AIProvider):
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        
        self.model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
        
    async def understand_intent(self, user_request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""
        You are NOVA's intent understanding engine.
        User request: '{user_request}'
        Context: {json.dumps(context)}
        Extract the structured intent.
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=IntentSchema
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini error in understand_intent: {e}")
            raise

    async def generate_response(self, user_request: str, decision: str, evidence: Dict[str, Any]) -> str:
        prompt = f"""
        You are NOVA, the intelligence layer for everyday life.
        User said: "{user_request}"
        Decision: {decision}
        Evidence: {json.dumps(evidence)}
        
        Provide a concise, friendly, and human explanation. 
        Do not expose raw JSON or chain-of-thought.
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7
                )
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini error in generate_response: {e}")
            raise
            
    async def generate_requirements(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = f"""
        Convert this intent into a list of generic product requirements.
        Intent: {json.dumps(intent)}
        
        IMPORTANT:
        - If the intent specifies a number of people, scale the quantity accordingly.
        - Ensure requirements are realistic. For example, if it's for 6 people, you might need more packs.
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=RequirementSchema
                )
            )
            res_dict = json.loads(response.text)
            return res_dict.get("requirements", [])
        except Exception as e:
            print(f"Gemini error in generate_requirements: {e}")
            raise
