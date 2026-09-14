import pytest
import asyncio
from backend.intent.intent_service import IntentReconciliationService
from backend.inventory.inventory_service import InventoryService
from backend.commerce.swiggy_adapter import SwiggyInstamartAdapter

class MockInventoryService(InventoryService):
    def __init__(self, mock_data):
        super().__init__()
        self.mock_data = mock_data

    def get_all(self):
        return self.mock_data

class MockCommerceAdapter(SwiggyInstamartAdapter):
    async def search_products(self, query, **kwargs):
        # Return mock results
        if "unavailable" in query.lower():
            raise Exception("Commerce unavailable")
        return [{
            "id": "mock_id_123",
            "name": f"Fresh {query}",
            "price": 100,
            "image": "img_url"
        }]
        
    async def get_product(self, product_id):
        return {
            "id": product_id,
            "name": "Mock Product",
            "price": 100
        }

async def mock_llm_reconcile(self, intent_text):
    import re
    # simple mock for testing
    match = re.search(r"for (\d+)", intent_text)
    servings = int(match.group(1)) if match else 2
    return {
        "intent": {"action": "COOK", "servings": servings},
        "pantry": {"available": [], "uncertain": []},
        "shopping": {"items": []},
        "decision": {"state": "DO_NOTHING"}
    }

@pytest.mark.asyncio
async def test_servings_pani_puri():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv)
    svc.reconcile_intent = mock_llm_reconcile.__get__(svc, IntentReconciliationService)
    res = await svc.reconcile_intent("I want to make pani puri for 4 people")
    assert res["intent"]["servings"] == 4

@pytest.mark.asyncio
async def test_servings_pasta():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv)
    svc.reconcile_intent = mock_llm_reconcile.__get__(svc, IntentReconciliationService)
    res = await svc.reconcile_intent("I want to make pasta for 6 people")
    assert res["intent"]["servings"] == 6

@pytest.mark.asyncio
async def test_servings_biryani():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv)
    svc.reconcile_intent = mock_llm_reconcile.__get__(svc, IntentReconciliationService)
    res = await svc.reconcile_intent("I want to make biryani for 12 people")
    assert res["intent"]["servings"] == 12

@pytest.mark.asyncio
async def test_cart_merge_behavior():
    adapter = MockCommerceAdapter()
    adapter.carts = {"test_cart": [{"id": "prod_1", "quantity": 1}]}
    await adapter.add_to_cart("test_cart", "prod_1", 2)
    
    assert adapter.carts["test_cart"][0]["quantity"] == 3
