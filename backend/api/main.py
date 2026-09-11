from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
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

decision_engine = DecisionEngine(
    budget_service=budget_service,
    policy_service=policy_service,
    inventory_service=inventory_service,
    session_service=session_service
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
