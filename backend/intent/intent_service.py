import json
import re
from typing import Dict, Any, List, Optional, Tuple

class IntentReconciliationService:
    def __init__(self, inventory_service=None, ai_service=None, commerce_adapter=None):
        self.inventory_service = inventory_service
        self.ai_service = ai_service
        self.commerce_adapter = commerce_adapter

    async def reconcile_intent(self, intent_text: str) -> Dict[str, Any]:
        print(f"[IntentReconciliationService] Reconciling intent: {intent_text}")
        
        # We will use self.ai_service if possible, but actually we can just call it via Gemini/Bedrock.
        # But wait, ai_service has generic `understand_intent` and `generate_requirements` which are not tuned for the exact JSON we need.
        # It's better to construct the AI call here. 
        # I'll just use self.ai_service.gemini or fallback.
        # We need a custom prompt to get the exact requirements.
        
        provider = None
        if hasattr(self.ai_service, 'gemini') and self.ai_service.gemini.has_key:
            provider = self.ai_service.gemini
        elif hasattr(self.ai_service, 'fallback'):
            provider = self.ai_service.fallback
            
        prompt = f"""
        Extract the cooking intent from the following user request and generate the recipe requirements.
        User request: "{intent_text}"
        
        Respond ONLY with a valid JSON object matching this schema EXACTLY:
        {{
            "intent": {{
                "action": "COOK",
                "target": "<dish name>",
                "servings": <number (extracted from request, default to 2 only if NOT specified)>
            }},
            "recipe": {{
                "name": "<dish name>",
                "requiredItems": [
                    {{"name": "<ingredient name>", "quantity": <number, scaled for servings>, "unit": "<unit>", "required": <boolean, false if optional garnish/topping>, "search_query": "<simple query for search>"}}
                ]
            }}
        }}
        """
        
        try:
            import os
            provider_type = os.environ.get("LLM_PROVIDER", "gemini").lower()
            
            if provider_type == "bedrock":
                import boto3
                client = boto3.client('bedrock-runtime', region_name=os.environ.get("AWS_REGION", "us-east-1"))
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt}]
                })
                response = client.invoke_model(
                    body=body,
                    modelId=os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
                    accept="application/json",
                    contentType="application/json"
                )
                res_body = json.loads(response.get('body').read())
                text_out = res_body.get('content', [{}])[0].get('text', '{}')
                if "```json" in text_out:
                    text_out = text_out.split("```json")[1].split("```")[0]
                parsed_ai = json.loads(text_out)
            else:
                import google.generativeai as genai
                model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                parsed_ai = json.loads(response.text)
        except Exception as e:
            print(f"[IntentReconciliationService] LLM parsing failed: {e}")
            import re
            
            # Simple regex fallback to preserve servings and dish
            dish_match = re.search(r"make (.+?)(?: for|$)", intent_text.lower())
            dish_name = dish_match.group(1).strip() if dish_match else intent_text
            
            serving_match = re.search(r"for (\d+)", intent_text.lower())
            servings = int(serving_match.group(1)) if serving_match else 2

            parsed_ai = {
                "intent": {"action": "COOK", "target": dish_name.title(), "servings": servings},
                "recipe": {
                    "name": dish_name.title(),
                    "requiredItems": []
                }
            }

        pantry_items = self.inventory_service.get_all() if self.inventory_service else []
        
        available = []
        shopping_items = []
        uncertain = []
        subtotal = 0
        
        recipe_items = parsed_ai.get("recipe", {}).get("requiredItems", [])
        
        for item in recipe_items:
            # We don't force optional items into shopping plan
            if not item.get("required", True):
                continue
                
            in_pantry = False
            is_uncertain = False
            for p in pantry_items:
                if p.get("name") and (item["search_query"].lower() in p["name"].lower() or item["name"].lower() in p["name"].lower()):
                    # check logic
                    days_remaining = p.get("days_remaining", 0)
                    confidence = p.get("confidence", 1.0)
                    
                    if days_remaining > 2 and confidence > 0.6:
                        available.append(p)
                        in_pantry = True
                    elif confidence <= 0.6:
                        uncertain.append(p)
                        is_uncertain = True
                    break
            
            if not in_pantry and not is_uncertain:
                if self.commerce_adapter:
                    try:
                        results = await self.commerce_adapter.search_products(item["search_query"])
                        if results:
                            # Pick the most sensible pack (e.g. avoid 5L unless requested)
                            best_match = results[0]
                            for r in results:
                                if "5l" not in r.get("name", "").lower() and "5kg" not in r.get("name", "").lower():
                                    best_match = r
                                    break
                                    
                            qty = 1 # Recommended purchase pack quantity is usually 1 pack
                            price = best_match.get("price", 0)
                            
                            shopping_items.append({
                                "id": best_match.get("id"),
                                "name": best_match.get("name"),
                                "price": price,
                                "quantity": qty,
                                "required_amount": f"{item.get('quantity', 1)} {item.get('unit', '')}",
                                "reason": f"Your pantry does not show enough for this meal.",
                                "imageUrl": best_match.get("image") or best_match.get("imageUrl")
                            })
                            subtotal += price * qty
                    except Exception as e:
                        print(f"[IntentReconciliationService] Search failed for {item['search_query']}: {e}")
        
        state = "DO_NOTHING"
        if shopping_items:
            state = "ASK"
        elif uncertain:
            state = "ASK"
            
        return {
            "intent": parsed_ai.get("intent"),
            "recipe": parsed_ai.get("recipe"),
            "pantry": {
                "available": available,
                "uncertain": uncertain
            },
            "shopping": {
                "items": shopping_items,
                "subtotal": subtotal
            },
            "decision": {
                "state": state
            }
        }
