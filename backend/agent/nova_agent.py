from typing import Dict, Any

class NovaAgent:
    def __init__(self, ai_service, decision_engine, commerce_adapter, inventory_service, budget_service, audit_service):
        self.ai_service = ai_service
        self.decision_engine = decision_engine
        self.commerce = commerce_adapter
        self.inventory = inventory_service
        self.budget = budget_service
        self.audit = audit_service
        
    async def handle_request(self, user_request: str) -> str:
        # 1. AI Understand Intent
        context = {"budget": await self.budget.get_remaining_budget()}
        intent = await self.ai_service.understand_intent(user_request, context)
        
        # 2. Extract requirement
        reqs = await self.ai_service.generate_requirements(intent)
        if not reqs:
            return "I couldn't figure out what you needed."
            
        all_evidence = []
        any_auto = False
        
        for req in reqs:
            # 3. Search Catalog
            products = await self.commerce.search_products(req["query"])
            if not products:
                all_evidence.append({
                    "product": req["query"],
                    "decision": "BLOCKED",
                    "reasons": ["Product not found in catalog."]
                })
                continue
                
            product = products[0]
            
            # 4. Deterministic Decision
            decision_context = {"confidence": intent.get("confidence", 1.0) > 0.8 and "HIGH" or "LOW"}
            decision, reasons = await self.decision_engine.evaluate(product, decision_context)
            
            # Log to audit
            self.audit.log_decision(product["name"], decision, reasons)
            
            evidence = {
                "product": product["name"],
                "price": product["price"],
                "decision": decision,
                "reasons": reasons
            }
            all_evidence.append(evidence)
            
            # 5. Execute if AUTO
            if decision == "AUTO":
                try:
                    any_auto = True
                    cart_id = await self.commerce.create_cart()
                    # In a real app we'd add the item to cart
                    await self.commerce.add_to_cart(cart_id, product["id"])
                    await self.commerce.checkout(cart_id)
                    await self.budget.record_spend(product["price"])
                    self.inventory.add_to_pantry(product.get("category", "Grocery"), product["name"], 1.0, "pack")
                except Exception as e:
                    # Downgrade to ASK if checkout fails
                    print(f"Checkout failed: {e}")
                    decision = "ASK"
                    all_evidence[-1]["decision"] = "ASK"
                    all_evidence[-1]["reasons"].append(f"Checkout failed: {str(e)}")
                    any_auto = False
                
        # 6. AI Generate Human Response
        # For simplicity in demo, if multiple items, combine decisions or let AI summarize
        # Let's pass the overall intent and evidence
        decision_summary = "AUTO" if any_auto else all_evidence[0]["decision"] if all_evidence else "ASK"
        response = await self.ai_service.generate_response(user_request, decision_summary, {"items": all_evidence})
        return response
