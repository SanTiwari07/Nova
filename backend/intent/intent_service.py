import os
import json
import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple

class IntentReconciliationService:
    def __init__(self, inventory_service=None, ai_service=None, commerce_adapter=None):
        self.inventory_service = inventory_service
        self.ai_service = ai_service
        self.commerce_adapter = commerce_adapter

    async def reconcile_intent(self, intent_text: str) -> Dict[str, Any]:
        """
        Dynamically analyzes a meal, cooking, or household activity intent.
        Decomposes the goal into required ingredients/items, queries the live household
        inventory, reconciles available vs missing stock, and finds commerce products
        for missing items.
        """
        print(f"[IntentReconciliationService] Reconciling intent: {intent_text}")
        
        prompt = f"""You are NOVA, a household autopilot assistant.
Analyze this meal preparation or cooking request: "{intent_text}"
Extract the dish name, number of servings (default to 2 if unspecified), and the 3 to 5 essential primary grocery ingredients.
Distinguish core required ingredients (required: true) from optional items (required: false).
For each ingredient, provide a clean, concise grocery search query (e.g. "pani puri pack", "chickpeas", "pani puri masala", "potatoes", "pasta", "pasta sauce").
Do not include tap water. Never suggest non-food or personal care items.

Respond ONLY with a valid JSON object matching this schema EXACTLY:
{{
    "intent": {{
        "action": "COOK",
        "target": "<dish name>",
        "servings": <number>
    }},
    "recipe": {{
        "name": "<dish name>",
        "requiredItems": [
            {{"name": "<ingredient name>", "quantity": <number>, "unit": "<unit>", "required": <boolean>, "search_query": "<simple search query>"}}
        ]
    }}
}}
"""
        parsed_ai = None
        provider_type = os.environ.get("LLM_PROVIDER", "gemini").lower()
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")

        # 1. Try Gemini LLM
        if provider_type == "gemini" and api_key and not api_key.startswith("your_") and not api_key.startswith("placeholder") and api_key != "fake":
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                text = response.text.strip()
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                parsed_ai = json.loads(text)
            except Exception as e:
                print(f"[IntentReconciliationService] Gemini call failed: {e}")

        # 2. Try AWS Bedrock
        elif provider_type == "bedrock":
            try:
                import boto3
                client = boto3.client('bedrock-runtime', region_name=os.environ.get("AWS_REGION", "us-east-1"))
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "temperature": 0.2,
                    "messages": [{"role": "user", "content": prompt}]
                })
                response = client.invoke_model(
                    body=body,
                    modelId=os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
                    accept="application/json",
                    contentType="application/json"
                )
                res_body = json.loads(response.get('body').read())
                text_out = res_body.get('content', [{}])[0].get('text', '{}')
                if "```json" in text_out:
                    text_out = text_out.split("```json")[1].split("```")[0].strip()
                parsed_ai = json.loads(text_out)
            except Exception as e:
                print(f"[IntentReconciliationService] Bedrock call failed: {e}")

        # Extract deterministic meal info from intent_text
        text_lower = intent_text.lower()
        requested_meal = ""
        if "biryani" in text_lower:
            requested_meal = "biryani"
        elif "pani puri" in text_lower or "panipuri" in text_lower or "golgappa" in text_lower:
            requested_meal = "pani puri"
        elif "pasta" in text_lower or "macaroni" in text_lower or "penne" in text_lower:
            requested_meal = "pasta"
        elif "maggi" in text_lower or "noodles" in text_lower:
            requested_meal = "maggi"
        elif "chai" in text_lower or "tea" in text_lower:
            requested_meal = "chai"
        elif "dosa" in text_lower:
            requested_meal = "dosa"

        # Validate Gemini's output against the requested meal
        if parsed_ai and requested_meal:
            llm_target = parsed_ai.get("intent", {}).get("target", "").lower()
            llm_recipe_name = parsed_ai.get("recipe", {}).get("name", "").lower()
            
            # If the requested meal is NOT in the LLM's target/recipe name, reject it
            if requested_meal not in llm_target and requested_meal not in llm_recipe_name:
                print(f"[IntentReconciliationService] Rejecting LLM output due to mismatch. Requested: {requested_meal}, LLM: {llm_target}")
                parsed_ai = None # Force fallback

        # 3. Dynamic Knowledge Layer (used if LLM is offline or returns empty or invalid)
        if not parsed_ai or not parsed_ai.get("recipe", {}).get("requiredItems"):
            parsed_ai = self._infer_meal_recipe(intent_text)
            
        if not parsed_ai:
             return {
                 "intent": {"action": "REQUIRE_CLARIFICATION", "target": "Unknown", "servings": 2},
                 "recipe": {"name": "Unknown", "requiredItems": []},
                 "pantry": {"available": [], "uncertain": []},
                 "shopping": {"items": [], "subtotal": 0},
                 "decision": {"state": "REQUIRE_CLARIFICATION"}
             }

        pantry_items = self.inventory_service.get_all() if self.inventory_service else []
        
        available = []
        shopping_items = []
        missing_candidates = []
        uncertain = []
        subtotal = 0
        
        recipe_items = parsed_ai.get("recipe", {}).get("requiredItems", [])
        
        for item in recipe_items:
            # We don't force optional garnish items into shopping plan
            if not item.get("required", True):
                continue
            item_name_lower = item.get("name", "").lower().strip()
            if item_name_lower in ["water", "tap water", "potable water", "warm water", "cold water", "boiling water", "ice"]:
                continue
                
            matched_pantry_item = self._match_pantry_item(item, pantry_items)
            
            if matched_pantry_item:
                days_remaining = matched_pantry_item.get("days_remaining", 7)
                confidence = matched_pantry_item.get("confidence", 1.0)
                status = matched_pantry_item.get("status", "HEALTHY")
                quantity = matched_pantry_item.get("quantity", 0)
                
                # If pantry has healthy stock and quantity > 0
                if status == "HEALTHY" or (quantity > 0 and days_remaining >= 2 and confidence > 0.5):
                    available.append({
                        "name": matched_pantry_item.get("name"),
                        "category": matched_pantry_item.get("category"),
                        "quantity": quantity,
                        "unit": matched_pantry_item.get("unit"),
                        "status": status,
                        "days_remaining": days_remaining,
                        "required_name": item.get("name")
                    })
                elif confidence <= 0.5 or (status == "LOW" and quantity < 0.2):
                    uncertain.append({
                        "name": matched_pantry_item.get("name"),
                        "category": matched_pantry_item.get("category"),
                        "quantity": quantity,
                        "unit": matched_pantry_item.get("unit"),
                        "status": status,
                        "required_name": item.get("name")
                    })
            else:
                missing_candidates.append(item)

        # Resolve missing items concurrently for fast agent response
        async def _resolve_missing_item(item, idx):
            if not self.commerce_adapter:
                return None
            query = item.get("search_query") or item.get("name")
            try:
                results = await self.commerce_adapter.search_products(query)
                if not results:
                    words = [w for w in query.split() if len(w) > 2]
                    if words:
                        results = await self.commerce_adapter.search_products(words[0])
                
                if results:
                    best_match = results[0]
                    for r in results:
                        name_l = r.get("name", "").lower()
                        if "5l" not in name_l and "5kg" not in name_l and "bulk" not in name_l:
                            best_match = r
                            break
                    qty = 1
                    price = float(best_match.get("price", 0))
                    img = best_match.get("image") or best_match.get("imageUrl")
                    return {
                        "id": best_match.get("id"),
                        "product_id": best_match.get("id"),
                        "name": best_match.get("name"),
                        "brand": best_match.get("brand"),
                        "price": price,
                        "quantity": qty,
                        "required_amount": f"{item.get('quantity', 1)} {item.get('unit', '')}".strip(),
                        "reason": f"Missing from your household pantry for {parsed_ai.get('recipe', {}).get('name', 'this meal')}.",
                        "imageUrl": img,
                        "image": img,
                        "category": best_match.get("category")
                    }
                else:
                    return {
                        "id": f"req_{idx}",
                        "name": item.get("name").title(),
                        "price": 0,
                        "quantity": 1,
                        "required_amount": f"{item.get('quantity', 1)} {item.get('unit', '')}".strip(),
                        "reason": "Not in pantry; check catalog for alternatives.",
                        "imageUrl": None,
                        "image": None
                    }
            except Exception as e:
                print(f"[IntentReconciliationService] Search failed for '{query}': {e}")
                return None

        if missing_candidates:
            resolved_results = await asyncio.gather(*[_resolve_missing_item(it, i) for i, it in enumerate(missing_candidates)])
            for res_item in resolved_results:
                if res_item:
                    shopping_items.append(res_item)
                    subtotal += float(res_item.get("price", 0)) * int(res_item.get("quantity", 1))
        
        state = "DO_NOTHING"
        if shopping_items:
            # check if any restricted categories
            blocked = False
            for item in shopping_items:
                cat = (item.get("category") or "").upper()
                if cat in ["ALCOHOL", "TOBACCO"]:
                    blocked = True
                    break
            if blocked:
                state = "BLOCKED"
            elif subtotal > 1500:
                state = "ASK" 
            else:
                state = "AUTO"
        elif uncertain:
            state = "ASK"
            
        matched_act = parsed_ai.get("recipe", {}).get("name") or parsed_ai.get("intent", {}).get("target", "Meal Preparation")
        available_in_pantry = [
            {
                "item": a.get("name") or a.get("required_name"),
                "matched_product": a.get("name"),
                "quantity": a.get("quantity"),
                "unit": a.get("unit"),
                "status": a.get("status"),
                "days_remaining": a.get("days_remaining", 7)
            }
            for a in available
        ]
        missing_items = [
            {
                "item": it.get("name"),
                "search_query": it.get("search_query") or it.get("name"),
                "priority": "HIGH" if it.get("required", True) else "LOW"
            }
            for it in missing_candidates
        ]
        suggested_queries = [it.get("search_query") or it.get("name") for it in missing_candidates]

        return {
            "intent": parsed_ai.get("intent"),
            "recipe": parsed_ai.get("recipe"),
            "pantry": {
                "available": available,
                "uncertain": uncertain
            },
            "shopping": {
                "items": shopping_items,
                "subtotal": round(subtotal, 2)
            },
            "decision": {
                "state": state
            },
            # Compatibility properties for testing and backward compatibility
            "activity_detected": True,
            "matched_activity": matched_act,
            "requirements": [it.get("name") for it in recipe_items],
            "available_in_pantry": available_in_pantry,
            "missing_items": missing_items,
            "suggested_queries": suggested_queries,
            "reconciliation_summary": f"Reconciled {matched_act}: {len(available)} available, {len(missing_candidates)} missing."
        }

    def _match_pantry_item(self, req_item: Dict[str, Any], pantry_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Intelligent fuzzy matcher between recipe ingredient requirement and live pantry items.
        Matches by keyword stems, categories, and tags.
        """
        req_name = req_item.get("name", "").lower()
        req_query = req_item.get("search_query", "").lower()
        full_req = f"{req_name} {req_query}"
        
        # Tokenize requirement into core word stems
        stopwords = {"for", "and", "fresh", "organic", "whole", "pack", "boiled", "mashed", "refined", "leaves", "powder", "paste", "pure", "diced"}
        req_tokens = [w for w in re.findall(r"\w+", full_req) if len(w) > 2 and w not in stopwords]
        
        # Define semantic equivalence groups
        SYNONYMS = {
            "potato": ["potato", "potatoes", "batata", "aloo"],
            "oil": ["oil", "sunflower", "refined", "ghee", "butter"],
            "salt": ["salt", "namak"],
            "spice": ["spice", "spices", "masala", "chilli", "haldi", "mirch", "jeera", "turmeric"],
            "chickpeas": ["chickpeas", "chana", "kabuli", "peas"],
            "rice": ["rice", "basmati", "chawal"],
            "atta": ["atta", "flour", "wheat", "gehu"],
            "milk": ["milk", "doodh", "dairy"],
            "tea": ["tea", "chai", "patti"],
            "sugar": ["sugar", "cheeni", "gur", "jaggery"],
            "pasta": ["pasta", "macaroni", "penne", "spaghetti"],
            "maggi": ["maggi", "noodles", "ramen"],
            "puri": ["puri", "pani puri", "golgappa", "shells"],
            "dal": ["dal", "toor", "moong", "lentils", "pulses"]
        }
        
        for p in pantry_items:
            p_name = p.get("name", "").lower()
            p_cat = p.get("category", "").lower()
            p_tags = [t.lower() for t in p.get("tags", [])]
            p_full = f"{p_name} {p_cat} {' '.join(p_tags)}"
            
            # 1. Direct substring match
            if req_name in p_name or (len(req_query) > 3 and req_query in p_name):
                return p
                
            # 2. Check semantic equivalence
            for group_key, group_words in SYNONYMS.items():
                req_has_group = any(w in full_req for w in group_words)
                pantry_has_group = any(w in p_full for w in group_words)
                if req_has_group and pantry_has_group:
                    # Guard: don't match "puri" with "oil" even if "oil" is used for frying
                    if "puri" in full_req and "oil" in p_full and "puri" not in p_full:
                        continue
                    if "chana" in full_req and "toor" in p_full and "chana" not in p_full:
                        continue
                    return p
                    
            # 3. Token stem matching
            for token in req_tokens:
                stem = token.rstrip("es").rstrip("s")
                if len(stem) >= 3 and (stem in p_name or stem in p_cat or any(stem in t for t in p_tags)):
                    return p
                    
        return None

    def _infer_meal_recipe(self, intent_text: str) -> Dict[str, Any]:
        """
        Intelligent meal decomposition knowledge base when LLM provider is offline.
        Covers panipuri, pasta, maggi, biryani, breakfast, chai, sandwiches, pizza, etc.
        """
        text = intent_text.lower()
        
        # Extract servings
        serving_match = re.search(r"for\s+(\d+)", text)
        servings = int(serving_match.group(1)) if serving_match else 2
        
        # 1. Panipuri / Golgappa
        if any(w in text for w in ["panipuri", "pani puri", "golgappa", "puchka"]):
            return {
                "intent": {"action": "COOK", "target": "Panipuri", "servings": servings},
                "recipe": {
                    "name": "Panipuri",
                    "requiredItems": [
                        {"name": "Pani Puri Shells / Puri", "quantity": 1, "unit": "pack", "required": True, "search_query": "pani puri"},
                        {"name": "White Chickpeas (Kabuli Chana)", "quantity": 1, "unit": "pack", "required": True, "search_query": "chickpeas"},
                        {"name": "Potatoes", "quantity": 2 * servings, "unit": "units", "required": True, "search_query": "potato"},
                        {"name": "Pani Puri Masala & Spices", "quantity": 1, "unit": "pack", "required": True, "search_query": "pani puri masala"},
                        {"name": "Cooking Oil", "quantity": 0.1, "unit": "L", "required": True, "search_query": "sunflower oil"},
                        {"name": "Salt", "quantity": 0.05, "unit": "kg", "required": True, "search_query": "salt"}
                    ]
                }
            }
            
        # 2. Pasta
        if any(w in text for w in ["pasta", "macaroni", "penne"]):
            return {
                "intent": {"action": "COOK", "target": "Pasta", "servings": servings},
                "recipe": {
                    "name": "Pasta",
                    "requiredItems": [
                        {"name": "Macaroni Pasta", "quantity": 1, "unit": "pack", "required": True, "search_query": "pasta"},
                        {"name": "Pasta & Pizza Sauce", "quantity": 1, "unit": "bottle", "required": True, "search_query": "pasta sauce"},
                        {"name": "Mozzarella Cheese Blend", "quantity": 1, "unit": "pack", "required": True, "search_query": "cheese"},
                        {"name": "Cooking Oil / Butter", "quantity": 0.05, "unit": "L", "required": True, "search_query": "sunflower oil"},
                        {"name": "Salt", "quantity": 0.02, "unit": "kg", "required": True, "search_query": "salt"}
                    ]
                }
            }
            
        # 3. Maggi / Noodles
        if any(w in text for w in ["maggi", "noodles"]):
            return {
                "intent": {"action": "COOK", "target": "Maggi Noodles", "servings": servings},
                "recipe": {
                    "name": "Maggi Noodles",
                    "requiredItems": [
                        {"name": "Maggi 2-Minute Noodles", "quantity": max(1, servings), "unit": "packs", "required": True, "search_query": "maggi noodles"},
                        {"name": "Cooking Oil", "quantity": 0.02, "unit": "L", "required": True, "search_query": "sunflower oil"},
                        {"name": "Mixed Spices", "quantity": 1, "unit": "pinch", "required": False, "search_query": "spices"}
                    ]
                }
            }
            
        # 4. Biryani
        if "biryani" in text:
            dish_name = "Biryani"
            items = [
                {"name": "Basmati Rice", "quantity": 0.5 * servings, "unit": "kg", "required": True, "search_query": "basmati rice"},
                {"name": "Biryani Masala", "quantity": 1, "unit": "pack", "required": True, "search_query": "biryani masala"},
                {"name": "Cooking Oil or Ghee", "quantity": 0.1, "unit": "L", "required": True, "search_query": "sunflower oil"},
                {"name": "Curd", "quantity": 1, "unit": "pack", "required": True, "search_query": "curd"},
                {"name": "Onion", "quantity": 1, "unit": "kg", "required": True, "search_query": "onion"}
            ]
            if "chicken" in text:
                dish_name = "Chicken Biryani"
                items.append({"name": "Chicken", "quantity": 0.5 * servings, "unit": "kg", "required": True, "search_query": "chicken"})
            elif "veg" in text or "vegetable" in text:
                dish_name = "Veg Biryani"
                items.append({"name": "Mixed Vegetables", "quantity": 0.5 * servings, "unit": "kg", "required": True, "search_query": "mixed vegetables"})
            else:
                items.append({"name": "Potatoes", "quantity": 1 * servings, "unit": "units", "required": True, "search_query": "potato"})
                
            return {
                "intent": {"action": "COOK", "target": dish_name, "servings": servings},
                "recipe": {
                    "name": dish_name,
                    "requiredItems": items
                }
            }

        # 5. Chai / Tea
        if any(w in text for w in ["chai", "tea"]):
            return {
                "intent": {"action": "COOK", "target": "Masala Chai", "servings": servings},
                "recipe": {
                    "name": "Masala Chai",
                    "requiredItems": [
                        {"name": "Tea Leaves", "quantity": 0.02, "unit": "kg", "required": True, "search_query": "tea"},
                        {"name": "Milk", "quantity": 0.25 * servings, "unit": "L", "required": True, "search_query": "milk"},
                        {"name": "Sugar", "quantity": 0.05, "unit": "kg", "required": True, "search_query": "sugar"}
                    ]
                }
            }

        # 6. Breakfast
        if "breakfast" in text:
            return {
                "intent": {"action": "COOK", "target": "Household Breakfast", "servings": servings},
                "recipe": {
                    "name": "Household Breakfast",
                    "requiredItems": [
                        {"name": "Fresh Milk", "quantity": 0.5, "unit": "L", "required": True, "search_query": "milk"},
                        {"name": "Tea Gold", "quantity": 1, "unit": "pack", "required": True, "search_query": "tea"},
                        {"name": "Whole Wheat Atta", "quantity": 0.5, "unit": "kg", "required": True, "search_query": "atta"},
                        {"name": "Cooking Oil", "quantity": 0.1, "unit": "L", "required": True, "search_query": "sunflower oil"}
                    ]
                }
            }

        # 7. Sandwich
        if any(w in text for w in ["sandwich", "sandwiches", "toast"]):
            return {
                "intent": {"action": "COOK", "target": "Grilled Sandwiches", "servings": servings},
                "recipe": {
                    "name": "Grilled Sandwiches",
                    "requiredItems": [
                        {"name": "Bread Loaf", "quantity": 1, "unit": "pack", "required": True, "search_query": "bread"},
                        {"name": "Butter or Cheese", "quantity": 1, "unit": "pack", "required": True, "search_query": "cheese"},
                        {"name": "Potatoes", "quantity": 2, "unit": "units", "required": True, "search_query": "potato"},
                        {"name": "Salt & Spices", "quantity": 1, "unit": "pinch", "required": True, "search_query": "spices"}
                    ]
                }
            }

        # 8. Potato dishes ("cook something with potatoes")
        if "potato" in text or "potatoes" in text or "aloo" in text:
            return {
                "intent": {"action": "COOK", "target": "Aloo Sabzi & Parathas", "servings": servings},
                "recipe": {
                    "name": "Aloo Sabzi & Parathas",
                    "requiredItems": [
                        {"name": "Potatoes", "quantity": 3, "unit": "units", "required": True, "search_query": "potato"},
                        {"name": "Whole Wheat Atta", "quantity": 0.5, "unit": "kg", "required": True, "search_query": "atta"},
                        {"name": "Cooking Oil", "quantity": 0.1, "unit": "L", "required": True, "search_query": "sunflower oil"},
                        {"name": "Spices & Masala", "quantity": 1, "unit": "pack", "required": True, "search_query": "spices"},
                        {"name": "Salt", "quantity": 0.05, "unit": "kg", "required": True, "search_query": "salt"}
                    ]
                }
            }

        # Generic extraction
        dish_match = re.search(r"(?:make|making|cook|cooking|prepare|preparing|have|having|eat|eating)\s+([a-zA-Z\s]+?)(?:\s+for|\s+tonight|\s+today|$)", text)
        dish_name = dish_match.group(1).strip().title() if dish_match else "Custom Meal"
        
        return {
            "intent": {"action": "COOK", "target": dish_name, "servings": servings},
            "recipe": {
                "name": dish_name,
                "requiredItems": [
                    {"name": dish_name, "quantity": 1, "unit": "pack", "required": True, "search_query": dish_name.lower()},
                    {"name": "Cooking Oil", "quantity": 0.05, "unit": "L", "required": True, "search_query": "sunflower oil"},
                    {"name": "Salt", "quantity": 0.02, "unit": "kg", "required": True, "search_query": "salt"}
                ]
            }
        }
