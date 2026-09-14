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
        if "unavailable" in query.lower():
            return []
        return [{
            "id": f"mock_id_{query.replace(' ', '_')}",
            "name": f"Fresh {query}",
            "price": 100,
            "image": "img_url",
            "category": kwargs.get("category", "General")
        }]

@pytest.fixture(autouse=True)
def disable_llm(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "none")

@pytest.mark.asyncio
async def test_1_biryani():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make biryani")
    assert res["recipe"]["name"] == "Biryani"

@pytest.mark.asyncio
async def test_2_pani_puri():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make pani puri")
    assert res["recipe"]["name"] == "Panipuri"

@pytest.mark.asyncio
async def test_3_pasta_4_people():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make pasta for 4 people")
    assert res["recipe"]["name"] == "Pasta"
    assert res["intent"]["servings"] == 4

@pytest.mark.asyncio
async def test_4_biryani_6_people():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make chicken biryani for 6 people")
    assert res["recipe"]["name"] == "Chicken Biryani"
    assert res["intent"]["servings"] == 6

@pytest.mark.asyncio
async def test_5_llm_rejection(monkeypatch):
    import os
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    
    import backend.intent.intent_service as intent_svc
    class FakeResponse:
        text = '```json\n{"intent": {"action": "COOK", "target": "Pani Puri", "servings": 2}, "recipe": {"name": "Pani Puri", "requiredItems": []}}\n```'
    
    class FakeModel:
        def __init__(self, *args, **kwargs): pass
        def generate_content(self, *args, **kwargs): return FakeResponse()
        
    class FakeGenai:
        GenerativeModel = FakeModel
        class GenerationConfig:
            def __init__(self, *args, **kwargs): pass
        def configure(self, *args, **kwargs): pass
        
    monkeypatch.setattr(intent_svc, "genai", FakeGenai(), raising=False)
    
    inv = MockInventoryService([])
    svc = intent_svc.IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make biryani")
    assert res["recipe"]["name"] == "Biryani"

@pytest.mark.asyncio
async def test_6_biryani_pantry():
    inv = MockInventoryService([
        {"name": "India Gate Basmati Rice", "category": "grocery", "quantity": 5, "unit": "kg", "days_remaining": 30, "status": "HEALTHY", "confidence": 0.9},
        {"name": "Fortune Sunflower Oil", "category": "grocery", "quantity": 2, "unit": "L", "days_remaining": 15, "status": "HEALTHY", "confidence": 0.9}
    ])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make biryani")
    
    avail_names = [a["name"].lower() for a in res["pantry"]["available"]]
    assert any("rice" in n for n in avail_names)
    assert any("oil" in n for n in avail_names)
    
    shopping_names = [s["name"].lower() for s in res["shopping"]["items"]]
    assert not any("rice" in n for n in shopping_names)
    assert not any("oil" in n for n in shopping_names)

@pytest.mark.asyncio
async def test_10_canonical_schema():
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make dosa")
    
    assert "intent" in res
    assert "recipe" in res
    assert "pantry" in res
    assert "shopping" in res
    assert "decision" in res
    assert "available" in res["pantry"]
    assert "items" in res["shopping"]

@pytest.mark.asyncio
async def test_12_everything_available():
    inv = MockInventoryService([
        {"name": "Maggi Noodles", "category": "grocery", "quantity": 10, "unit": "packs", "days_remaining": 30, "status": "HEALTHY", "confidence": 0.9},
        {"name": "Sunflower Oil", "category": "grocery", "quantity": 2, "unit": "L", "days_remaining": 15, "status": "HEALTHY", "confidence": 0.9},
        {"name": "Salt", "category": "grocery", "quantity": 1, "unit": "kg", "days_remaining": 50, "status": "HEALTHY", "confidence": 0.9},
        {"name": "Spices", "category": "grocery", "quantity": 1, "unit": "kg", "days_remaining": 50, "status": "HEALTHY", "confidence": 0.9}
    ])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=MockCommerceAdapter())
    res = await svc.reconcile_intent("I want to make maggi")
    
    assert len(res["shopping"]["items"]) == 0
    assert res["decision"]["state"] == "DO_NOTHING"

@pytest.mark.asyncio
async def test_13_ask_threshold():
    class HighPriceCommerce(MockCommerceAdapter):
        async def search_products(self, query, **kwargs):
            return [{
                "id": "exp_1",
                "name": f"Expensive {query}",
                "price": 2000,
                "image": "img_url"
            }]
            
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=HighPriceCommerce())
    res = await svc.reconcile_intent("I want to make maggi")
    assert res["decision"]["state"] == "ASK"

@pytest.mark.asyncio
async def test_14_restricted():
    class AlcoholCommerce(MockCommerceAdapter):
        async def search_products(self, query, **kwargs):
            return [{
                "id": "alcohol_1",
                "name": f"Beer",
                "price": 200,
                "image": "img_url",
                "category": "Alcohol"
            }]
            
    inv = MockInventoryService([])
    svc = IntentReconciliationService(inventory_service=inv, commerce_adapter=AlcoholCommerce())
    res = await svc.reconcile_intent("I want to make maggi")
    assert res["decision"]["state"] == "BLOCKED"
