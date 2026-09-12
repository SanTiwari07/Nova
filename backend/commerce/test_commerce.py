"""
Comprehensive test suite for NOVA commerce, product categorization, catalog filtering,
cart lifecycle with quantity controls, budget enforcement, and demo reset.
"""

import pytest
import asyncio
from backend.commerce.swiggy_adapter import SwiggyInstamartAdapter, infer_product_category
from backend.budget.budget_service import BudgetService


@pytest.fixture
def adapter():
    return SwiggyInstamartAdapter()


@pytest.fixture
def budget():
    return BudgetService()


# ── CATEGORY INFERENCE TESTS ──────────────────────────────────────────────────

def test_infer_product_category_milk():
    cat, tags = infer_product_category("Amul Taaza Toned Milk 1L", "Amul")
    assert cat == "Milk & Dairy"
    assert "milk" in tags


def test_infer_product_category_noodles():
    cat, tags = infer_product_category("Maggi 2-Minute Masala Instant Noodles 280g", "Nestle")
    assert cat == "Instant Noodles"
    assert "noodles" in tags


def test_infer_product_category_grains():
    cat, tags = infer_product_category("Aashirvaad Superior MP Atta 5kg", "Aashirvaad")
    assert cat == "Atta & Rice"
    assert "atta" in tags


def test_infer_product_category_oil():
    cat, tags = infer_product_category("Fortune Sunlite Refined Sunflower Oil 1L", "Fortune")
    assert cat == "Cooking Oils"
    assert "oil" in tags


def test_infer_product_category_cleaning():
    cat, tags = infer_product_category("Surf Excel Matic Front Load Detergent 1kg", "Surf Excel")
    assert cat == "Cleaning & Toiletries"
    assert "cleaning" in tags


def test_infer_product_category_tea_staples():
    cat, tags = infer_product_category("Tata Tea Gold 500g", "Tata")
    assert cat == "Tea & Staples"
    assert "tea" in tags


# ── SIMULATED / DEMO CATALOG TESTS ───────────────────────────────────────────

def test_simulated_catalog_completeness(adapter):
    products = adapter._get_simulated_catalog()
    assert len(products) >= 50
    # Verify all items have required normalized attributes
    for p in products:
        assert p["id"] is not None
        assert p["name"] is not None
        assert p["price"] > 0
        assert p["category"] is not None
        assert p["is_demo"] is True
        assert p["retailer"] == "demo_catalog"


def test_catalog_category_filtering(adapter):
    # Filter milk
    milk_items = adapter._get_simulated_catalog(category="milk")
    assert len(milk_items) > 0
    for p in milk_items:
        assert "milk" in p["category"].lower() or "milk" in p["name"].lower() or any("milk" in t for t in p["tags"])

    # Filter all items returns everything
    all_items = adapter._get_simulated_catalog(category="all")
    assert len(all_items) >= 50


def test_catalog_search(adapter):
    results = adapter._get_simulated_catalog(query="maggi")
    assert len(results) > 0
    for p in results:
        assert "maggi" in p["name"].lower() or "maggi" in (p.get("brand") or "").lower()


def test_catalog_search_and_category(adapter):
    # Searching for atta within grains category
    results = adapter._get_simulated_catalog(query="aashirvaad", category="grains")
    assert len(results) > 0
    for p in results:
        assert "aashirvaad" in p["name"].lower() or "aashirvaad" in p["brand"].lower()


# ── CART LIFECYCLE & QUANTITY CONTROLS ─────────────────────────────────────────

def test_cart_add_and_quantity(adapter):
    async def _run():
        cart_id = await adapter.create_cart()
        sim = adapter._get_simulated_catalog()
        prod_id = sim[0]["id"]
        price = sim[0]["price"]

        # 1. Add item with quantity 2
        cart = await adapter.add_to_cart(cart_id, prod_id, quantity=2)
        assert cart["item_count"] == 2
        assert cart["subtotal"] == round(price * 2, 2)
        assert len(cart["items"]) == 1

        # 2. Add same item again (quantity increments)
        cart = await adapter.add_to_cart(cart_id, prod_id, quantity=1)
        assert cart["item_count"] == 3
        assert cart["subtotal"] == round(price * 3, 2)

        # 3. Update quantity directly
        cart = await adapter.update_cart_quantity(cart_id, prod_id, quantity=5)
        assert cart["item_count"] == 5
        assert cart["subtotal"] == round(price * 5, 2)

        # 4. Decrease quantity
        cart = await adapter.update_cart_quantity(cart_id, prod_id, quantity=1)
        assert cart["item_count"] == 1
        assert cart["subtotal"] == round(price, 2)

        # 5. Remove item completely
        cart = await adapter.remove_from_cart(cart_id, prod_id)
        assert cart["item_count"] == 0
        assert cart["subtotal"] == 0.0
        assert len(cart["items"]) == 0

    asyncio.run(_run())


def test_checkout_total_calculation(adapter):
    async def _run():
        cart_id = await adapter.create_cart()
        sim = adapter._get_simulated_catalog()

        item1 = sim[0]
        item2 = sim[1]

        await adapter.add_to_cart(cart_id, item1["id"], quantity=2)
        await adapter.add_to_cart(cart_id, item2["id"], quantity=1)

        expected_total = (item1["price"] * 2) + (item2["price"] * 1)
        order = await adapter.checkout(cart_id)

        assert order["status"] == "CONFIRMED"
        assert order["total"] == round(expected_total, 2)
        assert len(order["items"]) == 2

    asyncio.run(_run())
