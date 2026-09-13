"""
Comprehensive Test Suite for NOVA Strands Autonomous Household Decision Agent.
Verifies all 3 Hero Scenarios and all critical decision engine safety boundaries:
1. Milk Auto-Buy (Hero Scenario 1: LOW stock -> AUTO -> simulated checkout -> audit log)
2. Oil Restraint (Hero Scenario 2: HEALTHY stock -> DO_NOTHING -> zero commerce -> audit log)
3. Maggi Intent Reconciliation (Hero Scenario 3: meal intent -> pantry check -> buy missing only)
4. Expensive product requires human confirmation (Price > ₹500 -> ASK)
5. Policy-blocked category prevention (Alcohol / blocked -> BLOCKED)
6. Insufficient remaining budget protection (Spend > Budget -> ASK)
7. Low tracking confidence safety gate (Confidence LOW -> ASK)
8. Offline Strands fallback mode deterministic execution
9. Unknown catalog product error handling
10. Commerce checkout failure graceful degradation
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from inventory.inventory_service import InventoryService
from budget.budget_service import BudgetService
from policy.policy_service import PolicyService
from decision.decision_service import DecisionEngine
from audit.audit_service import AuditService
from commerce.swiggy_adapter import SwiggyInstamartAdapter
from intent.intent_service import IntentReconciliationService
from reminders.reminder_service import ReminderEngine
from savings.savings_engine import SavingsEngine
from agent.tools import create_nova_tools
from agent.nova_agent import NovaAgent
from user.session_service import UserSessionService


@pytest.fixture
def fresh_environment():
    """Sets up an isolated, deterministic environment for each test."""
    inv = InventoryService()
    budget = BudgetService()
    policy = PolicyService()
    audit = AuditService()
    session = UserSessionService()
    session.set_autonomy_profile("FULL_AUTOPILOT")
    
    commerce = SwiggyInstamartAdapter()
    decision = DecisionEngine(
        budget_service=budget,
        policy_service=policy,
        inventory_service=inv,
        session_service=session
    )
    intent = IntentReconciliationService(inventory_service=inv)
    reminders = ReminderEngine()
    savings = SavingsEngine()

    tools = create_nova_tools(
        inventory_service=inv,
        budget_service=budget,
        policy_service=policy,
        commerce_adapter=commerce,
        history_service=None,
        decision_engine=decision,
        audit_service=audit,
        session_service=session,
        intent_service=intent,
        reminder_engine=reminders,
        savings_engine=savings,
    )

    agent = NovaAgent(
        ai_service=None,
        decision_engine=decision,
        commerce_adapter=commerce,
        inventory_service=inv,
        budget_service=budget,
        audit_service=audit,
        session_service=session,
        intent_service=intent,
        reminder_engine=reminders,
        savings_engine=savings,
    )

    return {
        "inv": inv,
        "budget": budget,
        "policy": policy,
        "audit": audit,
        "session": session,
        "commerce": commerce,
        "decision": decision,
        "intent": intent,
        "reminders": reminders,
        "savings": savings,
        "tools": {t.tool_spec["name"]: t for t in tools},
        "agent": agent
    }


@pytest.mark.asyncio
async def test_hero_1_milk_auto_buy(fresh_environment):
    """
    Scenario 1: Amul Taaza Milk is LOW (0.3L left, 0.6L daily consumption -> 0.5 days).
    Evaluating purchase of milk should return AUTO, execute simulated transaction,
    deduct budget, increment pantry, and log audit entry.
    """
    env = fresh_environment
    tools = env["tools"]
    inv = env["inv"]
    budget = env["budget"]
    audit = env["audit"]

    # Verify initial pantry stock is low
    milk_pantry = next((item for item in inv.get_all() if "milk" in item["name"].lower()), None)
    assert milk_pantry is not None
    assert milk_pantry["status"] == "LOW"

    # Search for milk product
    search_fn = tools["search_catalog"]
    products = await search_fn(query="amul milk")
    assert len(products) > 0
    milk_prod = products[0]

    initial_budget = budget.get_status()["remaining"]
    initial_log_count = len(audit.get_recent(10))

    # Execute purchase tool
    purchase_fn = tools["evaluate_and_execute_purchase"]
    result = await purchase_fn(
        product_id=milk_prod["product_id"],
        quantity=1,
        reason="Autonomous daily milk replenishment"
    )

    assert result["verdict"] == "AUTO"
    assert result["executed"] is True
    assert result["total_cost"] == milk_prod["price"]

    # Budget must be deducted
    new_budget = budget.get_status()["remaining"]
    assert new_budget == initial_budget - milk_prod["price"]

    # Audit log must record AUTO decision
    logs = audit.get_recent(10)
    assert len(logs) > initial_log_count
    assert any(l["decision"] == "AUTO" for l in logs)


@pytest.mark.asyncio
async def test_hero_2_oil_restraint(fresh_environment):
    """
    Scenario 2: Fortune Sunflower Oil has 2.1L in stock with 0.07L/day consumption (~30 days).
    NOVA must exercise restraint: decision is DO_NOTHING, zero commerce action,
    budget is fully preserved, and restraint is recorded in the audit trail.
    """
    env = fresh_environment
    inv = env["inv"]
    budget = env["budget"]
    audit = env["audit"]
    decision_engine = env["decision"]

    # Check oil in pantry
    oil_item = next((item for item in inv.get_all() if "oil" in item["name"].lower()), None)
    assert oil_item is not None
    assert oil_item["status"] == "HEALTHY"
    assert oil_item["days_remaining"] >= 20

    # Decision engine direct check for oil
    oil_product = {
        "id": "prod_000030",
        "name": "Fortune Sunlite Refined Sunflower Oil 1L",
        "category": "Cooking Oils",
        "price": 155
    }
    decision, reasons = await decision_engine.evaluate(oil_product, {"confidence": "HIGH"})
    assert decision == "DO_NOTHING"
    assert any("enough inventory" in r.lower() for r in reasons)

    # Agent restraint tool execution
    restraint_fn = env["tools"]["record_restraint_decision"]
    res = restraint_fn(
        item_or_category=oil_product["name"],
        reason="Pantry has 2.1L in stock (~30 days remaining)."
    )
    assert res["verdict"] == "DO_NOTHING"
    assert res["action"] == "RESTRAINT_RECORDED"

    # Audit log contains DO_NOTHING
    logs = audit.get_recent(5)
    assert any(l["decision"] == "DO_NOTHING" for l in logs)


@pytest.mark.asyncio
async def test_hero_3_maggi_intent_reconciliation(fresh_environment):
    """
    Scenario 3: Meal Intent "I want to make Maggi tonight".
    NOVA decomposes the activity, checks the pantry, finds oil and spices in stock,
    identifies noodles as missing, and only purchases the missing noodles.
    """
    env = fresh_environment
    intent_service = env["intent"]
    tools = env["tools"]

    reconciliation = await intent_service.reconcile_intent("I want to make Maggi tonight")
    assert reconciliation["activity_detected"] is True
    assert "Maggi" in reconciliation["matched_activity"]
    
    # Cooking oil and salt are in pantry
    available = [a["item"].lower() for a in reconciliation["available_in_pantry"]]
    assert any("oil" in a for a in available)
    
    # Noodles are missing
    missing = [m["item"].lower() for m in reconciliation["missing_items"]]
    assert any("noodle" in m for m in missing)

    # Only purchase the missing item
    search_fn = tools["search_catalog"]
    results = await search_fn(query="maggi noodles")
    assert len(results) > 0
    
    purchase_fn = tools["evaluate_and_execute_purchase"]
    res = await purchase_fn(
        product_id=results[0]["product_id"],
        quantity=1,
        reason="Meal ingredient fulfillment"
    )
    assert res["verdict"] == "AUTO"
    assert res["executed"] is True
    assert res["total_cost"] < 100


@pytest.mark.asyncio
async def test_expensive_product_requires_ask(fresh_environment):
    """
    Items above the auto-buy limit (e.g. ₹500) must NEVER be auto-purchased.
    Must return ASK and executed=False.
    """
    env = fresh_environment
    tools = env["tools"]
    budget = env["budget"]
    initial_budget = budget.get_status()["remaining"]

    # Search for an item and evaluate a large quantity that exceeds ₹500 limit
    search_fn = tools["search_catalog"]
    products = await search_fn(query="atta")
    assert len(products) > 0
    atta = products[0]

    purchase_fn = tools["evaluate_and_execute_purchase"]
    unit_price = atta.get("price", 100)
    qty = max(2, int(600 / unit_price) + 1)
    res = await purchase_fn(
        product_id=atta["product_id"],
        quantity=qty,
        reason="Bulk purchase attempt"
    )

    assert res["verdict"] == "ASK"
    assert res["executed"] is False
    assert any("limit" in r.lower() or "auto-buy" in r.lower() for r in res["reasons"])
    # Budget must remain untouched
    assert budget.get_status()["remaining"] == initial_budget


@pytest.mark.asyncio
async def test_blocked_policy_category(fresh_environment):
    """
    Restricted/disallowed categories must evaluate to BLOCKED.
    Zero spend, executed=False.
    """
    env = fresh_environment
    policy = env["policy"]
    decision = env["decision"]

    blocked_item = {
        "id": "prod_liquor_999",
        "name": "Single Malt Scotch Whisky 750ml",
        "category": "Alcohol & Spirits",
        "price": 3200
    }

    verdict, reasons = await decision.evaluate(blocked_item, {"confidence": "HIGH"})
    assert verdict == "BLOCKED"
    assert any("restricted" in r.lower() or "policy" in r.lower() or "blocked" in r.lower() for r in reasons)


@pytest.mark.asyncio
async def test_budget_exceeded_requires_ask(fresh_environment):
    """
    When purchase exceeds total remaining monthly budget, safety gate must trigger.
    """
    env = fresh_environment
    budget = env["budget"]
    decision = env["decision"]

    # Exhaust budget almost entirely
    await budget.record_spend(budget.get_status()["remaining"] - 50)
    assert budget.get_status()["remaining"] == 50

    item = {
        "id": "prod_ghee_01",
        "name": "Amul Pure Ghee 1L",
        "category": "Dairy",
        "price": 350 # Greater than ₹50 remaining
    }

    verdict, reasons = await decision.evaluate(item, {"confidence": "HIGH"})
    assert verdict == "ASK"
    assert any("budget" in r.lower() for r in reasons)


@pytest.mark.asyncio
async def test_low_confidence_requires_ask(fresh_environment):
    """
    When inventory tracking confidence is LOW, auto-buy must be deferred to user confirmation.
    """
    env = fresh_environment
    decision = env["decision"]

    item = {
        "id": "prod_000109",
        "name": "Amul Taaza Milk 1L",
        "category": "Milk",
        "price": 68
    }

    verdict, reasons = await decision.evaluate(item, {"confidence": "LOW"})
    assert verdict == "ASK"
    assert any("confidence" in r.lower() for r in reasons)


@pytest.mark.asyncio
async def test_offline_fallback_mode_execution(fresh_environment):
    """
    Verifies that when LLM provider is disabled / credentials missing,
    NovaAgent executes the 3 hero scenarios deterministically via its tool runner.
    """
    env = fresh_environment
    agent = env["agent"]

    # Force fallback mode
    agent.agent = None

    # Test Milk query
    res_milk = await agent.handle_request("I need milk.", force_fallback=True)
    assert res_milk["status"] == "success"
    assert len(res_milk["tool_trace"]) >= 2
    assert any(t["tool"] == "evaluate_and_execute_purchase" for t in res_milk["tool_trace"])

    # Test Oil query
    res_oil = await agent.handle_request("Should I buy oil?", force_fallback=True)
    assert res_oil["status"] == "success"
    assert any("no need" in res_oil["response"].lower() or "enough" in res_oil["response"].lower() or "restraint" in res_oil["response"].lower() for _ in [1])
    assert any(t["tool"] == "record_restraint_decision" for t in res_oil["tool_trace"])

    # Test Maggi query
    res_maggi = await agent.handle_request("I want to make Maggi tonight.", force_fallback=True)
    assert res_maggi["status"] == "success"
    assert any(t["tool"] == "reconcile_activity_requirements" for t in res_maggi["tool_trace"])


@pytest.mark.asyncio
async def test_unknown_catalog_product_error_resilience(fresh_environment):
    """
    Evaluating purchase for a non-existent product ID returns error status without crashing.
    """
    env = fresh_environment
    purchase_fn = env["tools"]["evaluate_and_execute_purchase"]

    res = await purchase_fn(
        product_id="prod_non_existent_999999",
        quantity=1,
        reason="Invalid item test"
    )
    assert res["verdict"] == "ERROR"
    assert res["executed"] is False
    assert "not found" in res["reasons"][0]


@pytest.mark.asyncio
async def test_commerce_failure_graceful_handling(fresh_environment):
    """
    When the commerce adapter throws an unexpected checkout failure,
    the tool catches it, blocks spend deduction, and returns ASK with error details.
    """
    env = fresh_environment
    commerce = env["commerce"]
    budget = env["budget"]
    initial_budget = budget.get_status()["remaining"]
    tools = env["tools"]

    # Mock checkout failure
    commerce.checkout = AsyncMock(side_effect=RuntimeError("Instamart Gateway Timeout"))

    purchase_fn = tools["evaluate_and_execute_purchase"]
    res = await purchase_fn(
        product_id="prod_000109", # Amul milk
        quantity=1,
        reason="Failover test"
    )

    assert res["executed"] is False
    assert res["verdict"] == "ASK"
    assert any("timeout" in r.lower() or "error" in r.lower() for r in res["reasons"])
    # Budget was NOT deducted
    assert budget.get_status()["remaining"] == initial_budget


@pytest.mark.asyncio
async def test_generic_intent_reconciliation_poha(fresh_environment):
    """
    Generalized Intent Reconciliation:
    When user requests 'I am making poha tonight', intent reconciliation detects
    poha as missing while oil, salt, and spices are already available in stock.
    Only missing poha is queried and evaluated.
    """
    env = fresh_environment
    reconcile_fn = env["tools"]["reconcile_activity_requirements"]

    res = await reconcile_fn(intent="I am making poha tonight")
    assert "poha" in res["matched_activity"].lower()
    missing = [m["item"].lower() for m in res["missing_items"]]
    available = [a["item"].lower() for a in res["available_in_pantry"]]

    assert any("poha" in m for m in missing)
    assert any("oil" in a or "salt" in a for a in available)
    assert len(res["suggested_queries"]) > 0
    assert any("poha" in q.lower() for q in res["suggested_queries"])


@pytest.mark.asyncio
async def test_manage_household_reminder_tool(fresh_environment):
    """
    Strands Tool: manage_household_reminder
    Supports creating, listing, and completing household reminders dynamically.
    """
    env = fresh_environment
    rem_tool = env["tools"]["manage_household_reminder"]

    # 1. Create reminder
    create_res = rem_tool(
        action="create",
        title="Service Air Conditioner",
        message="Annual AC filter cleaning and coolant check",
        priority="HIGH"
    )
    assert create_res["status"].lower() == "success"
    rem_id = create_res["reminder"]["id"]

    # 2. List reminders
    list_res = rem_tool(action="list", status="ACTIVE")
    assert list_res["status"].lower() == "success"
    assert any(r["id"] == rem_id for r in list_res["reminders"])

    # 3. Complete reminder
    comp_res = rem_tool(action="complete", reminder_id=rem_id)
    assert comp_res["status"].lower() == "success"
    assert comp_res["reminder"]["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_update_household_policy_tool(fresh_environment):
    """
    Strands Tool: update_household_policy
    Supports mutating categories and spending limits via natural agent actions.
    """
    env = fresh_environment
    policy_tool = env["tools"]["update_household_policy"]
    policy = env["policy"]
    budget = env["budget"]

    # 1. Restrict category
    res = policy_tool(action="restrict_category", category="Electronics")
    assert res["status"].lower() == "success"
    assert "Electronics" in policy.restricted_categories

    # 2. Whitelist category
    res2 = policy_tool(action="whitelist_auto", category="Essentials")
    assert res2["status"].lower() == "success"
    assert "Essentials" in policy.automatic_categories

    # 3. Set limits
    res3 = policy_tool(action="set_limits", auto_limit=450.0)
    assert res3["status"].lower() == "success"
    assert budget.get_status()["auto_limit"] == 450.0


@pytest.mark.asyncio
async def test_update_pantry_stock_and_depletion_tool(fresh_environment):
    """
    Strands Tool: update_pantry_stock and report_item_depleted
    Allows dynamic household inventory synchronization through Strands tools.
    """
    env = fresh_environment
    stock_tool = env["tools"]["update_pantry_stock"]
    deplete_tool = env["tools"]["report_item_depleted"]
    inv = env["inv"]

    # 1. Add / restock item
    res = stock_tool(item_name="Poha", quantity=2.0, unit="kg")
    assert res["status"].lower() == "success"
    poha = inv.get_item_by_name("Poha")
    assert poha is not None
    assert poha["quantity"] == 2.0
    assert poha["status"] == "HEALTHY"

    # 2. Report depleted
    res2 = deplete_tool(item_name="Poha")
    assert res2["status"].lower() == "success"
    assert res2["item"]["quantity"] == 0.0
    assert res2["item"]["status"] == "LOW"


@pytest.mark.asyncio
async def test_agent_offline_dispatch_arbitrary_dish(fresh_environment):
    """
    NovaAgent Deterministic Tool Dispatcher:
    Validates that an unscripted cooking intent ('I want to cook pasta tonight')
    executes real Strands tools (reconciliation, catalog search, evaluation)
    without any hardcoded dish keywords in the agent router.
    """
    env = fresh_environment
    agent = env["agent"]

    result = await agent.invoke("I want to cook pasta tonight", force_fallback=True)
    assert result["status"] == "success"
    tools_called = [t["tool"] for t in result["tool_trace"]]
    assert "reconcile_activity_requirements" in tools_called
    assert "search_catalog" in tools_called
    assert "evaluate_and_execute_purchase" in tools_called
    assert "pasta" in result["response"].lower()


@pytest.mark.asyncio
async def test_agent_offline_dispatch_pantry_depletion(fresh_environment):
    """
    NovaAgent Deterministic Tool Dispatcher:
    Validates that 'We ran out of salt' triggers report_item_depleted
    and updates pantry status to LOW.
    """
    env = fresh_environment
    agent = env["agent"]
    inv = env["inv"]

    result = await agent.invoke("We ran out of salt", force_fallback=True)
    assert result["status"] == "success"
    tools_called = [t["tool"] for t in result["tool_trace"]]
    assert "report_item_depleted" in tools_called

    salt = inv.get_item_by_name("salt")
    assert salt is not None
    assert salt["quantity"] == 0.0
    assert salt["status"] == "LOW"

