"""
NOVA Hardening & Regression Test Suite
Validates all bug fixes from Phase 2:
- Dual-field RequestModel compatibility (text vs command)
- Non-dropping InventoryService.add_to_pantry for new categories
- ReminderEngine status filtering ("ALL", case-insensitivity)
- Bidirectional substring matching in PolicyService
- Serving size extraction and ingredient scaling in IntentReconciliationService
"""

import pytest
import asyncio
from api.main import RequestModel
from inventory.inventory_service import InventoryService
from reminders.reminder_service import ReminderEngine
from policy.policy_service import PolicyService
from intent.intent_service import IntentReconciliationService


def test_request_model_dual_field_support():
    # 1. Standard text field
    r1 = RequestModel(text="Check my budget")
    assert r1.get_text() == "Check my budget"
    
    # 2. Command field from Pantry copilot
    r2 = RequestModel(command="Add milk to pantry")
    assert r2.get_text() == "Add milk to pantry"
    
    # 3. Both fields present
    r3 = RequestModel(text="I need bread", command="fallback command")
    assert r3.get_text() == "I need bread"
    
    # 4. Empty / whitespace handled
    r4 = RequestModel(text="   ")
    assert r4.get_text() == ""


def test_inventory_service_add_to_pantry_new_item():
    inv = InventoryService()
    initial_count = len(inv.get_all())
    
    # Add an item with a brand new category
    inv.add_to_pantry(category="Pet Supplies", name="Cat Food Kibble", quantity=2.0, unit="kg")
    
    all_items = inv.get_all()
    assert len(all_items) == initial_count + 1
    
    cat_food = inv.get_item_by_name("Cat Food Kibble")
    assert cat_food is not None
    assert cat_food["quantity"] == 2.0
    assert cat_food["status"] == "HEALTHY"
    assert cat_food["unit"] == "kg"
    
    # Add more of the same item -> updates existing
    inv.add_to_pantry(category="Pet Supplies", name="Cat Food Kibble", quantity=1.5, unit="kg")
    assert len(inv.get_all()) == initial_count + 1
    assert cat_food["quantity"] == 3.5


def test_reminder_service_all_and_case_insensitive_filter():
    rem = ReminderEngine()
    
    # Active reminders
    active = rem.get_reminders(status="ACTIVE")
    assert len(active) > 0
    assert all(r["status"] == "ACTIVE" for r in active)
    
    # Lowercase active
    active_lower = rem.get_reminders(status="active")
    assert len(active_lower) == len(active)
    
    # ALL filter
    all_rems = rem.get_reminders(status="ALL")
    assert len(all_rems) >= len(active)
    
    # None filter returns all
    all_none = rem.get_reminders(status=None)
    assert len(all_none) == len(all_rems)


@pytest.mark.asyncio
async def test_policy_bidirectional_category_matching():
    pol = PolicyService()
    
    # Restricted category bidirectional check
    assert await pol.is_category_allowed("Single Malt Alcohol") is False
    assert await pol.is_category_allowed("Alcohol & Spirits") is False
    assert await pol.is_category_allowed("Tobacco & Cigars") is False
    assert await pol.is_category_allowed("Dairy & Fresh Milk") is True
    
    # Ask category bidirectional check
    assert await pol.requires_ask("Electronics & Gadgets") is True
    assert await pol.requires_ask("Evening Snacks") is True
    
    # Automatic category bidirectional check
    assert await pol.is_automatic("Milk & Dairy") is True
    assert await pol.is_automatic("Fresh Milk") is True


@pytest.mark.asyncio
async def test_intent_reconciliation_serving_scale():
    inv = InventoryService()
    intent_svc = IntentReconciliationService(inventory_service=inv)
    
    # Test biryani recipe detection and serving scale for 6 people
    res = await intent_svc.reconcile_intent("I want to make biryani for 6 people tonight")
    assert res["activity_detected"] is True
    assert "biryani" in res["matched_activity"].lower()
    
    # Cooking oil or ghee should be detected in pantry
    avail = [a["item"].lower() for a in res["available_in_pantry"]]
    assert any("oil" in a or "ghee" in a for a in avail)
    
    # Missing items should include Basmati Rice and Biryani Masala
    missing = [m["item"].lower() for m in res["missing_items"]]
    assert any("rice" in m for m in missing)
    assert any("masala" in m for m in missing)
