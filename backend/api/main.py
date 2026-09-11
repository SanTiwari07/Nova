# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Query, HTTPException
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os

from ai.ai_service import AIService
from decision.decision_service import DecisionEngine
from commerce.mock_adapter import MockCommerceAdapter
from inventory.inventory_service import InventoryService
from budget.budget_service import BudgetService
from policy.policy_service import PolicyService
from audit.audit_service import AuditService
from user.session_service import UserSessionService
from agent.nova_agent import NovaAgent

from catalog.product_repository import ProductRepository
from catalog.asset_repository import AssetRepository

# Amazon-first services
from amazon.history_service import MockAmazonHistoryProvider
from amazon.price_service import PriceService
from autopilot.monthly_service import MonthlyAutopilotService
from reminders.reminder_service import ReminderEngine
from savings.savings_engine import SavingsEngine

app = FastAPI(title="NOVA API")

# Mount static assets directory
assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
if not os.path.exists(assets_dir):
    os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Initialize Services
ai_service = AIService()
budget_service = BudgetService()
policy_service = PolicyService()
inventory_service = InventoryService()
commerce_adapter = MockCommerceAdapter()
audit_service = AuditService()
session_service = UserSessionService()

product_repo = ProductRepository()
asset_repo = AssetRepository()

# Amazon-first services
history_service = MockAmazonHistoryProvider()
price_service = PriceService()
reminder_engine = ReminderEngine()
savings_engine = SavingsEngine()

decision_engine = DecisionEngine(
    budget_service=budget_service,
    policy_service=policy_service,
    inventory_service=inventory_service,
    session_service=session_service
)

autopilot_service = MonthlyAutopilotService(
    budget_service=budget_service,
    policy_service=policy_service,
    inventory_service=inventory_service,
)

nova_agent = NovaAgent(
    ai_service=ai_service,
    decision_engine=decision_engine,
    commerce_adapter=commerce_adapter,
    inventory_service=inventory_service,
    budget_service=budget_service,
    audit_service=audit_service
)

class RequestModel(BaseModel):
    text: str

class LoginRequest(BaseModel):
    email: str

class ConnectRequest(BaseModel):
    provider: str
    
class AutonomyRequest(BaseModel):
    profile: str

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    session_service.login(req.email)
    return session_service.get_session_state()

@app.get("/api/auth/session")
async def get_session():
    return session_service.get_session_state()

@app.post("/api/auth/logout")
async def logout():
    session_service.logout()
    return {"status": "ok"}

@app.post("/api/onboarding/services")
async def connect_service(req: ConnectRequest):
    session_service.connect_service(req.provider)
    return session_service.get_session_state()

@app.post("/api/onboarding/autonomy")
async def set_autonomy(req: AutonomyRequest):
    session_service.set_autonomy_profile(req.profile)
    return session_service.get_session_state()

@app.post("/api/demo/reset")
async def reset_demo():
    session_service.reset()
    budget_service.reset()
    policy_service.reset()
    inventory_service.reset()
    audit_service.reset()
    reminder_engine.reset()
    commerce_adapter.carts = {}
    commerce_adapter.orders = {}
    return {"status": "ok"}

@app.post("/api/command")
async def process_command(req: RequestModel):
    response_text = await nova_agent.handle_request(req.text)
    return {"response": response_text}

@app.get("/api/budget")
async def get_budget():
    return {
        "monthly": budget_service.monthly_budget,
        "spent": budget_service.spent,
        "remaining": await budget_service.get_remaining_budget(),
        "auto_limit": budget_service.auto_limit
    }

@app.get("/api/pantry")
async def get_pantry():
    return inventory_service.get_all()

@app.get("/api/orders")
async def get_orders():
    return commerce_adapter.get_orders()

@app.get("/api/audit/activity")
async def get_activity():
    return audit_service.get_recent()

@app.get("/api/products")
async def get_products(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    return product_repo.get_all(skip=skip, limit=limit)

@app.get("/api/products/search")
async def search_products(q: str, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    return product_repo.search(query=q, skip=skip, limit=limit)

@app.get("/api/products/categories")
async def get_categories():
    return product_repo.get_categories()

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = product_repo.get_by_id(product_id)
    if product:
        return product
    return {"error": "Not found"}, 404

@app.get("/api/commerce/compare/{product_id}")
async def compare_commerce_options(product_id: str):
    import random
    product = product_repo.get_by_id(product_id)
    if not product:
        return {"error": "Product not found"}, 404
        
    offers = await commerce_adapter.compare_options(product_id)
    
    # Get inventory context
    pantry = inventory_service.get_all()
    cat = product.get("category", "")
    
    inventory_item = next((item for item in pantry if item["name"].lower() == cat.lower() or cat.lower() in item["name"].lower()), None)
    
    # Simple AI recommendation logic
    valid_offers = [o for o in offers if o["availability"] == "IN_STOCK"]
    if valid_offers:
        recommended_offer = min(valid_offers, key=lambda x: x["effectiveTotal"])
    else:
        recommended_offer = None
        
    budget = budget_service.monthly_budget
    auto_limit = budget_service.auto_limit
    
    return {
        "product": product,
        "context": {
            "householdRequirement": f"{random.randint(1, 3)} {product.get('unit', 'unit')}s" if not inventory_item else "Replenish supply",
            "estimatedInventory": inventory_item["status"] if inventory_item else "Unknown",
            "inventoryConfidence": inventory_item["confidence"] if inventory_item else 85,
            "budget": budget,
            "autoLimit": auto_limit
        },
        "offers": offers,
        "recommendation": {
            "retailerId": recommended_offer["retailerId"] if recommended_offer else None,
            "reason": [
                "Lowest effective price",
                "Matches required quantity",
                "Within your automatic purchase limit" if recommended_offer and recommended_offer["effectiveTotal"] <= auto_limit else "Exceeds automatic purchase limit"
            ]
        }
    }

@app.get("/api/products/{product_id}/assets")
async def get_product_assets(product_id: str):
    asset = asset_repo.get_asset_for_product(product_id)
    if asset:
        return asset
    
    product = product_repo.get_by_id(product_id)
    cat = product.get("category", "") if product else ""
    return {
        "thumbnail": asset_repo.get_fallback_for_category(cat) or asset_repo.get_generic_fallback(),
        "medium": asset_repo.get_fallback_for_category(cat) or asset_repo.get_generic_fallback(),
        "status": "fallback"
    }

class CartRequest(BaseModel):
    product_id: str

@app.get("/api/cart")
async def get_cart():
    if not commerce_adapter.carts:
        return {"items": []}
    cart_id = list(commerce_adapter.carts.keys())[0]
    return {"cart_id": cart_id, "items": commerce_adapter.carts[cart_id]}

@app.post("/api/cart/add")
async def add_to_cart(req: CartRequest):
    # Dummy cart for demo single user
    if not commerce_adapter.carts:
        cart_id = await commerce_adapter.create_cart()
    else:
        cart_id = list(commerce_adapter.carts.keys())[0]
    await commerce_adapter.add_to_cart(cart_id, req.product_id)
    return {"cart_id": cart_id, "items": commerce_adapter.carts[cart_id]}

@app.post("/api/checkout")
async def checkout():
    if not commerce_adapter.carts:
        return {"error": "No active cart"}
    cart_id = list(commerce_adapter.carts.keys())[0]
    # Remove from active carts immediately to prevent double processing
    cart_items = commerce_adapter.carts.pop(cart_id, None)
    if cart_items is None:
         return {"error": "Cart already checked out"}
         
    # Temporarily put back for commerce adapter to process, 
    # but in a real app we pass the items directly or use a lock.
    commerce_adapter.carts[cart_id] = cart_items
    try:
        order = await commerce_adapter.checkout(cart_id)
        # Deduct from budget
        await budget_service.record_spend(order["total"])
        del commerce_adapter.carts[cart_id]
        return order
    except Exception as e:
        # Rollback
        commerce_adapter.carts[cart_id] = cart_items
        return {"error": str(e)}, 500

# ─────────────────────────────────────────────────────────────────────────────
# AMAZON-FIRST ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/purchase-history")
async def get_purchase_history():
    """Recurring household product intelligence from Amazon purchase history."""
    return {
        "products": history_service.get_recurring_products(),
        "source": "AMAZON_MOCK",
        "label": "Demo data",
    }

@app.get("/api/price-watch")
async def get_price_watch():
    """Price intelligence for watched household products."""
    return {
        "items": price_service.get_price_watch_items(),
        "source": "AMAZON_MOCK",
        "label": "Demo data",
    }

@app.get("/api/savings")
async def get_savings():
    """Savings opportunities for current household shopping plan."""
    return savings_engine.get_savings_opportunities()

@app.get("/api/reminders")
async def get_reminders(status: Optional[str] = "ACTIVE"):
    """Household reminders by status."""
    return {
        "reminders": reminder_engine.get_reminders(status=status),
        "count": len(reminder_engine.get_reminders(status=status)),
    }

class ReminderActionRequest(BaseModel):
    action: str  # snooze | complete | dismiss
    snooze_hours: Optional[int] = 24

@app.post("/api/reminders/{reminder_id}/action")
async def reminder_action(reminder_id: str, req: ReminderActionRequest):
    """Snooze, complete, or dismiss a reminder."""
    if req.action == "snooze":
        result = reminder_engine.snooze(reminder_id, hours=req.snooze_hours)
    elif req.action == "complete":
        result = reminder_engine.complete(reminder_id)
    elif req.action == "dismiss":
        result = reminder_engine.dismiss(reminder_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {req.action}")
    if not result:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return result

@app.post("/api/autopilot/monthly-plan")
async def generate_monthly_plan():
    """Generate the monthly household Amazon shopping plan."""
    plan = await autopilot_service.generate_monthly_plan()
    return plan

class ApproveRequest(BaseModel):
    product_id: str
    approved: bool
    quantity: Optional[int] = None

@app.post("/api/autopilot/approve")
async def approve_autopilot_item(req: ApproveRequest):
    """Approve or reject an individual autopilot item."""
    if req.approved:
        # In a real integration: add to Amazon cart
        # For demo: record approval in audit
        audit_service.log_decision(
            req.product_id,
            "APPROVED_BY_USER",
            [f"User approved product {req.product_id}"]
        )
        return {"status": "APPROVED", "product_id": req.product_id, "label": "Ready for Amazon Cart"}
    else:
        audit_service.log_decision(
            req.product_id,
            "REJECTED_BY_USER",
            [f"User rejected product {req.product_id}"]
        )
        return {"status": "REJECTED", "product_id": req.product_id}

@app.get("/api/nova-cart")
async def get_nova_cart():
    """NOVA's intelligent household cart — the planned purchase set."""
    recurring = history_service.get_recurring_products()
    budget_remaining = await budget_service.get_remaining_budget()
    auto_limit = await budget_service.get_auto_buy_limit()

    nova_cart_items = []
    for product in recurring:
        days_until = product.get("days_until_needed", 30)
        if days_until > 10:
            continue  # Not needed yet

        current_price = product.get("current_price", 0)
        avg_price = product.get("avg_price", current_price)
        price_pct_above = ((current_price - avg_price) / avg_price * 100) if avg_price else 0
        requires_approval = current_price > auto_limit or product.get("confidence", 1.0) < 0.75

        nova_cart_items.append({
            **product,
            "quantity": product.get("typical_quantity", 1),
            "estimated_cost": current_price * product.get("typical_quantity", 1),
            "requires_approval": requires_approval,
            "price_pct_vs_avg": round(price_pct_above, 1),
            "decision": "ASK" if requires_approval else "AUTO",
            "reason": f"Usually purchased every {product.get('typical_interval_days', 28)} days. Expected in {days_until} days.",
        })

    total = sum(i["estimated_cost"] for i in nova_cart_items)

    return {
        "items": nova_cart_items,
        "total_estimated": total,
        "budget_remaining": budget_remaining,
        "auto_limit": auto_limit,
        "item_count": len(nova_cart_items),
        "approval_required_count": len([i for i in nova_cart_items if i["requires_approval"]]),
        "source": "AMAZON_MOCK",
        "label": "Demo data",
    }

class NovaCartItemRequest(BaseModel):
    product_id: str
    quantity: Optional[int] = 1

@app.post("/api/nova-cart/items")
async def add_nova_cart_item(req: NovaCartItemRequest):
    """Add an item to the NOVA household cart."""
    product = product_repo.get_by_id(req.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "added", "product_id": req.product_id, "quantity": req.quantity, "label": "Added to NOVA Cart"}

@app.delete("/api/nova-cart/items/{product_id}")
async def remove_nova_cart_item(product_id: str):
    """Remove an item from the NOVA household cart."""
    return {"status": "removed", "product_id": product_id}

@app.get("/api/household-status")
async def get_household_status():
    """Aggregated household status for the home page hero."""
    recurring = history_service.get_recurring_products()
    budget_remaining = await budget_service.get_remaining_budget()
    savings = savings_engine.get_savings_opportunities()
    active_reminders = reminder_engine.get_reminders(status="ACTIVE")

    due_soon = [p for p in recurring if p.get("days_until_needed", 30) <= 7]
    total_estimated = sum(p.get("current_price", 0) * p.get("typical_quantity", 1) for p in recurring if p.get("days_until_needed", 30) <= 20)

    return {
        "greeting_context": "Good evening",
        "status_headline": "Your household is almost ready for September.",
        "tracked_items": len(recurring),
        "items_due_soon": len(due_soon),
        "estimated_monthly_spend": round(total_estimated),
        "potential_savings": savings["total_potential_saving"],
        "budget_remaining": budget_remaining,
        "active_reminders": len(active_reminders),
        "attention_items": len([r for r in active_reminders if r["priority"] == "HIGH"]),
        "source": "AMAZON_MOCK",
    }
