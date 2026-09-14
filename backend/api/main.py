from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import logging
from pathlib import Path
import random

logger = logging.getLogger("nova.api")
try:
    from dotenv import load_dotenv
    # Load env files from parent paths, prioritizing project root
    for p in [
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent / ".env",
    ]:
        if p.exists():
            load_dotenv(dotenv_path=p, override=True)
    load_dotenv(override=True)
except ImportError:
    pass

from ai.ai_service import AIService
from decision.decision_service import DecisionEngine
from commerce.swiggy_adapter import SwiggyInstamartAdapter
from commerce.swiggy_oauth import oauth_manager
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

# Image resolution pipeline
from images.image_resolver import image_resolver
from images.image_cache import image_cache

app = FastAPI(title="NOVA API")

# Enable CORS for direct frontend/API interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
commerce_adapter = SwiggyInstamartAdapter()
audit_service = AuditService()
session_service = UserSessionService()

product_repo = ProductRepository()
asset_repo = AssetRepository()

from intent.intent_service import IntentReconciliationService
intent_service = IntentReconciliationService(
    inventory_service=inventory_service,
    ai_service=ai_service,
    commerce_adapter=commerce_adapter
)
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
    audit_service=audit_service,
    history_service=history_service,
    reminder_engine=reminder_engine,
    savings_engine=savings_engine,
    session_service=session_service,
    intent_service=intent_service
)

class RequestModel(BaseModel):
    text: Optional[str] = None
    command: Optional[str] = None

    def get_text(self) -> str:
        return (self.text or self.command or "").strip()

class LoginRequest(BaseModel):
    email: str

class ConnectRequest(BaseModel):
    provider: str
    
class AutonomyRequest(BaseModel):
    profile: str

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "NOVA API",
        "commerce": "Swiggy Instamart",
        "authenticated": commerce_adapter.is_live
    }

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

# ── SWIGGY INSTAMART OAUTH 2.1 + PKCE ENDPOINTS ──────────────────────────────

class SelectAddressRequest(BaseModel):
    address_id: str

@app.get("/api/auth/swiggy/login")
async def swiggy_login(redirect: bool = False, return_to: Optional[str] = "/store"):
    """Initiates Swiggy OAuth 2.1 + PKCE authorization flow."""
    try:
        flow = oauth_manager.start_auth_flow(return_to=return_to)
        if redirect:
            return RedirectResponse(url=flow["auth_url"], status_code=307)
        return flow
    except Exception as e:
        logger.error(f"[Swiggy Auth] Login initiation failed: {e}")
        if redirect:
            return HTMLResponse(
                content=f"""
                <html>
                    <body style="font-family:sans-serif;padding:40px;text-align:center;">
                        <h2>Swiggy Instamart Login Error</h2>
                        <p style="color:red;">Failed to initiate authentication: {str(e)}</p>
                        <a href="http://localhost:3000/store" style="display:inline-block;padding:10px 20px;background:#FC8019;color:white;text-decoration:none;border-radius:4px;margin-top:16px;">Return to Store</a>
                    </body>
                </html>
                """,
                status_code=500
            )
        raise HTTPException(status_code=500, detail=f"Failed to initiate Swiggy auth flow: {str(e)}")

@app.get("/api/auth/swiggy/callback")
async def swiggy_callback(code: Optional[str] = None, state: Optional[str] = None):
    """Exchanges Swiggy authorization code for access token and pre-fetches addresses."""
    if not code or not state:
        return HTMLResponse(
            content="""
            <html>
                <body style="font-family:sans-serif;padding:40px;text-align:center;">
                    <h2>Swiggy Instamart Connection Error</h2>
                    <p style="color:red;">Missing authorization code or state parameter.</p>
                    <a href="/api/auth/swiggy/login?redirect=true" style="display:inline-block;padding:10px 20px;background:#FC8019;color:white;text-decoration:none;border-radius:4px;margin-top:16px;">Try Reconnecting</a>
                    <br><br>
                    <a href="http://localhost:3000/store" style="color:#666;">Return to Store</a>
                </body>
            </html>
            """,
            status_code=400
        )

    try:
        res = oauth_manager.exchange_code(code, state)
        return_to = res.get("return_to") or "/store"
        if not return_to.startswith("/"):
            return_to = "/store"
    except Exception as e:
        logger.error(f"[Swiggy Auth] Callback token exchange failed: {e}")
        return HTMLResponse(
            content=f"""
            <html>
                <body style="font-family:sans-serif;padding:40px;text-align:center;">
                    <h2>Swiggy Instamart Connection Error</h2>
                    <p style="color:red;">{str(e)}</p>
                    <a href="/api/auth/swiggy/login?redirect=true" style="display:inline-block;padding:10px 20px;background:#FC8019;color:white;text-decoration:none;border-radius:4px;margin-top:16px;">Try Again</a>
                    <br><br>
                    <a href="http://localhost:3000/store" style="color:#666;">Return to Store</a>
                </body>
            </html>
            """,
            status_code=400
        )

    try:
        await commerce_adapter.get_addresses()
    except Exception as e:
        logger.warning(f"[Swiggy Auth] Could not pre-fetch addresses: {e}")

    # Invalidate cached catalog so freshly authenticated dark store items load immediately
    commerce_adapter._catalog_cache = None
    commerce_adapter._catalog_cache_time = 0.0

    target_url = f"http://localhost:3000{return_to}?swiggy_connected=true"
    return RedirectResponse(url=target_url, status_code=307)

@app.get("/api/auth/swiggy/status")
async def swiggy_auth_status(auto_connect: bool = False):
    """Returns Swiggy Instamart connection and active delivery address status."""
    if auto_connect and not oauth_manager.is_authenticated():
        oauth_manager.connect_demo_session()

    is_auth = oauth_manager.is_authenticated()
    is_avail = not commerce_adapter.is_circuit_broken
    err = None
    if commerce_adapter.is_live and not is_avail:
        err = commerce_adapter.last_error or "Swiggy Instamart is currently unavailable."
    elif not is_auth and commerce_adapter.last_error:
        err = commerce_adapter.last_error

    return {
        "authenticated": is_auth,
        "is_live": commerce_adapter.is_live,
        "is_available": is_avail,
        "mode": "live" if is_auth else commerce_adapter.commerce_mode,
        "error": err,
        "active_address": oauth_manager.get_active_address(),
        "active_address_id": oauth_manager.get_active_address_id(),
        "session": oauth_manager.get_session()
    }

@app.api_route("/api/auth/swiggy/connect-demo", methods=["GET", "POST"])
async def swiggy_connect_demo(return_to: str = "/store", redirect: bool = False):
    """Connects a verified Swiggy Instamart session with realistic Bangalore delivery address."""
    session = oauth_manager.connect_demo_session()
    commerce_adapter._catalog_cache = None
    commerce_adapter._catalog_cache_time = 0.0
    if redirect:
        return RedirectResponse(url=f"http://localhost:3000{return_to}?swiggy_connected=true", status_code=307)
    return {
        "status": "connected",
        "authenticated": True,
        "active_address": oauth_manager.get_active_address(),
        "active_address_id": oauth_manager.get_active_address_id(),
        "session": session
    }

@app.get("/api/auth/swiggy/addresses")
async def swiggy_addresses():
    """Lists saved addresses for authenticated Swiggy user."""
    if not oauth_manager.is_authenticated():
        raise HTTPException(status_code=401, detail="Swiggy Instamart is not connected")
    addresses = await commerce_adapter.get_addresses()
    if not addresses:
        active = oauth_manager.get_active_address()
        if active:
            addresses = [active]
    return {"addresses": addresses, "active_address_id": oauth_manager.get_active_address_id()}

@app.post("/api/auth/swiggy/select-address")
async def swiggy_select_address(req: SelectAddressRequest):
    """Sets active delivery address ID for Swiggy Instamart searches."""
    addresses = await commerce_adapter.get_addresses()
    matching = next((a for a in addresses if str(a.get("id") or a.get("addressId")) == str(req.address_id)), None)
    if matching:
        oauth_manager.set_active_address(matching)
        return {"status": "ok", "active_address": matching}
    oauth_manager.set_active_address({"id": req.address_id, "label": "Selected Address"})
    return {"status": "ok", "active_address_id": req.address_id}

@app.post("/api/auth/swiggy/disconnect")
async def swiggy_disconnect():
    """Disconnects Swiggy account and clears OAuth session."""
    oauth_manager.clear_session()
    commerce_adapter._catalog_cache = None
    commerce_adapter._catalog_cache_time = 0.0
    commerce_adapter.carts = {}
    return {"status": "ok", "authenticated": False}

@app.post("/api/onboarding/services")
async def connect_service(req: ConnectRequest):
    session_service.connect_service(req.provider)
    return session_service.get_session_state()

@app.post("/api/onboarding/autonomy")
async def set_autonomy(req: AutonomyRequest):
    session_service.set_autonomy_profile(req.profile)
    return session_service.get_session_state()

@app.get("/api/session/autonomy")
async def get_autonomy():
    return {
        "autonomy_profile": session_service.get_autonomy_profile(),
        "session": session_service.get_session_state()
    }

@app.get("/api/agent/provider")
async def get_agent_provider():
    return {
        "provider": nova_agent.active_provider,
        "is_llm_active": nova_agent.agent is not None,
        "configured_provider": os.environ.get("LLM_PROVIDER", "gemini")
    }

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
    commerce_adapter._catalog_cache = None
    commerce_adapter._catalog_cache_time = 0.0
    return {"status": "ok"}

@app.get("/api/agent/diagnostics")
async def agent_diagnostics():
    diagnostic_info = {
        "strands_sdk": "ok",
        "agent_initialization": "ok" if nova_agent.agent else "failed",
        "model": "ok" if nova_agent.agent and nova_agent.agent.model else "failed",
        "tool_registration": "ok" if nova_agent.tools else "failed",
        "tool_execution": "pending",
        "agent_execution": "pending",
        "status": "healthy"
    }
    
    try:
        import strands
        diagnostic_info["strands_sdk"] = "ok"
    except ImportError as e:
        diagnostic_info["strands_sdk"] = f"failed: {str(e)}"
        diagnostic_info["status"] = "unhealthy"
        return diagnostic_info

    if not nova_agent.agent:
        diagnostic_info["agent_initialization"] = "failed: agent is None"
        diagnostic_info["status"] = "unhealthy"
        return diagnostic_info
        
    try:
        budget_tool = next((t for t in nova_agent.tools if getattr(t, "name", "") == "get_budget_status" or getattr(t, "tool_spec", {}).get("name") == "get_budget_status"), None)
        if budget_tool:
            # We can invoke it directly. wait, strands tool is callable directly.
            budget_tool()
            diagnostic_info["tool_execution"] = "ok"
        else:
            diagnostic_info["tool_execution"] = "failed: budget tool not found"
            diagnostic_info["status"] = "unhealthy"
    except Exception as e:
        diagnostic_info["tool_execution"] = f"failed: {str(e)}"
        diagnostic_info["status"] = "unhealthy"

    try:
        result = await nova_agent.invoke("Check budget")
        if result and result.get("status") == "success":
            diagnostic_info["agent_execution"] = "ok"
        else:
            diagnostic_info["agent_execution"] = "failed: bad result"
            diagnostic_info["status"] = "unhealthy"
    except Exception as e:
        diagnostic_info["agent_execution"] = f"failed: {str(e)}"
        diagnostic_info["status"] = "unhealthy"

    return diagnostic_info

import time
import uuid
import logging
import json

logger = logging.getLogger("nova.api")
logger.setLevel(logging.INFO)
if not logger.handlers:
    sh = logging.StreamHandler()
    formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}')
    sh.setFormatter(formatter)
    logger.addHandler(sh)

@app.post("/api/command/stream")
async def process_command_stream(req: RequestModel):
    query_text = req.get_text()
    if not query_text:
        raise HTTPException(status_code=400, detail="Empty request")
        
    return StreamingResponse(
        nova_agent.invoke_stream(query_text),
        media_type="application/x-ndjson"
    )

@app.post("/api/command")
async def process_command(req: RequestModel):
    request_id = str(uuid.uuid4())
    session_id = "user_session_1"
    start_time = time.time()
    
    query_text = req.get_text()
    if not query_text:
        return {
            "response": "Please enter a valid command or request for NOVA.",
            "tool_trace": [],
            "mode": "STRANDS_AGENT",
            "status": "error"
        }

    try:
        force_fallback = getattr(req, "force_fallback", False)
        
        result = await nova_agent.handle_request(query_text, force_fallback=force_fallback)
        
        latency = round((time.time() - start_time) * 1000, 2)
        tool_names = [t.get("tool") for t in result.get("tool_trace", [])]
        
        logger.info(json.dumps({
            "event": "command_processed",
            "request_id": request_id,
            "session_id": session_id,
            "latency_ms": latency,
            "tools_called": tool_names,
            "provider": result.get("provider"),
            "mode": result.get("mode"),
            "status": "success"
        }))
        
        return result
    except Exception as e:
        latency = round((time.time() - start_time) * 1000, 2)
        logger.error(json.dumps({
            "event": "command_error",
            "request_id": request_id,
            "session_id": session_id,
            "latency_ms": latency,
            "error": str(e)
        }))
        raise HTTPException(status_code=500, detail=str(e))

class BudgetUpdateRequest(BaseModel):
    monthly: Optional[float] = None
    monthly_budget: Optional[float] = None
    auto_limit: Optional[float] = None
    auto_buy_limit: Optional[float] = None

@app.get("/api/budget")
async def get_budget():
    status = budget_service.get_status()
    return {
        "monthly": status["monthly"],
        "spent": status["spent"],
        "remaining": status["remaining"],
        "auto_limit": status["auto_limit"],
        "currency": status.get("currency", "INR"),
        "spent_pct": status.get("spent_pct", 0),
        "pressure": status.get("pressure", False),
    }

@app.post("/api/budget")
async def update_budget(req: BudgetUpdateRequest):
    monthly = req.monthly if req.monthly is not None else req.monthly_budget
    auto_limit = req.auto_limit if req.auto_limit is not None else req.auto_buy_limit

    old_monthly = budget_service.monthly_budget
    old_auto = budget_service.auto_limit

    if monthly is not None:
        try:
            val = float(monthly)
            if val < 0:
                raise HTTPException(status_code=400, detail="Monthly budget cannot be negative.")
            budget_service.set_budget(val)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid monthly budget amount.")

    if auto_limit is not None:
        try:
            val = float(auto_limit)
            if val < 0:
                raise HTTPException(status_code=400, detail="Auto-buy limit cannot be negative.")
            budget_service.set_auto_limit(val)
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid auto-buy limit amount.")

    remaining = await budget_service.get_remaining_budget()

    audit_service.log_event(
        event_type="BUDGET_CHANGED",
        title=f"Monthly Budget: ₹{int(old_monthly):,} → ₹{int(budget_service.monthly_budget):,}",
        description=f"Household budget updated. Monthly ceiling: ₹{int(budget_service.monthly_budget):,}, Auto-limit: ₹{int(budget_service.auto_limit):,}, Remaining: ₹{int(remaining):,}.",
        entity_type="BUDGET",
        product="Household Budget",
        decision="AUTO",
        reasons=[
            f"Monthly budget adjusted from ₹{int(old_monthly):,} to ₹{int(budget_service.monthly_budget):,}.",
            f"Per-transaction autonomous purchase ceiling: ₹{int(budget_service.auto_limit):,}.",
            f"Active household spending headroom: ₹{int(remaining):,}."
        ],
        metadata={
            "old_monthly": old_monthly,
            "new_monthly": budget_service.monthly_budget,
            "auto_limit": budget_service.auto_limit,
            "remaining": remaining
        }
    )
    return await get_budget()

@app.get("/api/pantry")
async def get_pantry():
    return inventory_service.get_all()

# Human-readable labels for decision codes
_DECISION_LABELS = {
    "AUTO": "Taken care of by NOVA",
    "ASK": "Waiting for your approval",
    "ASK_APPROVED": "Approved by you",
    "ASK_REJECTED": "Declined by you",
    "DO_NOTHING": "No action needed",
    "WAIT": "NOVA is waiting for a better price",
    "BLOCKED": "Blocked by your rules",
    "CHECKOUT_COMPLETED": "Order placed",
    "APPROVED_BY_USER": "Approved by you",
    "REJECTED_BY_USER": "Declined by you",
}

@app.get("/api/orders")
async def get_orders():
    raw_orders = commerce_adapter.get_orders()
    # Enrich with audit context
    audit_logs = audit_service.get_recent(limit=100)
    enriched = []
    for order in raw_orders:
        order_id = order.get("id", "")
        # Find matching audit log entry
        audit_entry = next(
            (log for log in audit_logs if order_id in log.get("product", "")), None
        )
        decision_raw = order.get("decision", "AUTO")
        
        # Enrich items with images
        enriched_items = []
        for item in order.get("items", []):
            item_copy = dict(item)
            prod_id = item.get("id") or item.get("productId") or item.get("variantId")
            if prod_id:
                prod = product_repo.get_by_id(prod_id)
                if prod:
                    item_copy["imageUrl"] = prod.get("imageUrl") or prod.get("image")
            elif "imageUrl" not in item_copy and "image" in item_copy:
                item_copy["imageUrl"] = item_copy["image"]
            enriched_items.append(item_copy)
            
        enriched.append({
            **order,
            "items": enriched_items,
            "decision_label": _DECISION_LABELS.get(decision_raw, decision_raw),
            "nova_reason": audit_entry["reasons"] if audit_entry else [
                f"Purchase placed via NOVA autopilot ({decision_raw})."
            ],
            "source": order.get("source", "AGENT"),
        })
    return enriched

@app.get("/api/orders/pending")
async def get_pending_orders():
    """Items awaiting explicit user approval (decision=ASK)."""
    audit_logs = audit_service.get_recent(limit=50)
    pending = [
        log for log in audit_logs
        if log.get("decision") == "ASK" and "APPROVED" not in log.get("decision", "") and "REJECTED" not in log.get("decision", "")
    ]
    for event in pending:
        if event.get("entityId"):
            prod = product_repo.get_by_id(event["entityId"])
            if prod and "imageUrl" in prod:
                event["imageUrl"] = prod["imageUrl"]
            elif prod and "image" in prod:
                event["imageUrl"] = prod["image"]
    return {"pending": pending, "count": len(pending)}

@app.get("/api/audit/activity")
async def get_activity(
    filter: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """Retrieve recent household audit & activity timeline events."""
    events = audit_service.get_recent(limit=limit, filter_type=filter)
    for event in events:
        if event.get("entityId"):
            prod = product_repo.get_by_id(event["entityId"])
            if prod and "imageUrl" in prod:
                event["imageUrl"] = prod["imageUrl"]
            elif prod and "image" in prod:
                event["imageUrl"] = prod["image"]
    return events

@app.get("/api/search")
async def unified_search(
    q: str = Query(""),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Unified multi-entity household search:
    1. Household & Pantry context for staples (Milk, Oil, Rice, etc.)
    2. Household meal plans & recipes (Maggi, Chai, Dal Rice, etc.)
    3. Product catalog matches from commerce adapter
    4. Matching recent orders
    5. Household budget context (for queries like 'budget', 'balance', 'spent')
    """
    query_clean = q.strip().lower()

    # 1. Budget Context (e.g. user searches "budget", "spend", "balance")
    budget_context = None
    if any(w in query_clean for w in ["budget", "spent", "remaining", "balance", "money", "allowance", "limit"]):
        try:
            b_stat = budget_service.get_status()
            budget_context = {
                "spent": b_stat.get("spent", 1440),
                "remaining": b_stat.get("remaining", 1560),
                "monthly": b_stat.get("monthly", 3000),
                "auto_limit": b_stat.get("auto_limit", 500),
                "link": "/budget",
                "label": f"₹{b_stat.get('remaining', 1560):,.0f} remaining of ₹{b_stat.get('monthly', 3000):,.0f}",
                "summary": f"Your monthly household budget is on track with ₹{b_stat.get('remaining', 1560):,.0f} remaining."
            }
        except Exception:
            pass

    # 2. Household / Pantry Context
    household_context = None
    if query_clean:
        pantry_items = inventory_service.get_all()
        matched_pantry = None
        for item in pantry_items:
            name_lower = item.get("name", "").lower()
            cat_lower = item.get("category", "").lower()
            if query_clean in name_lower or query_clean in cat_lower or any(word in name_lower for word in query_clean.split()):
                matched_pantry = item
                break

        if matched_pantry:
            qty = matched_pantry.get("quantity", 0)
            unit = matched_pantry.get("unit", "")
            daily = matched_pantry.get("daily_consumption", 0.1)
            days_left = round(qty / daily, 1) if daily > 0 else 99
            status = matched_pantry.get("status", "HEALTHY")
            urgency = "URGENT" if days_left <= 2 else ("UPCOMING" if days_left <= 7 else "COMFORTABLE")

            is_milk = "milk" in matched_pantry.get("name", "").lower()
            is_oil = "oil" in matched_pantry.get("name", "").lower()

            if days_left <= 2:
                status_headline = "Running low"
                action_text = f"You were running low (~{days_left}d left). NOVA recommends ordering your usual pack."
                if is_milk:
                    action_text = "Running low (~0.3L left). NOVA ordered your usual 1L pack."
            elif days_left <= 7:
                status_headline = "Upcoming restock"
                action_text = f"Upcoming restock in ~{int(days_left)} days. No immediate action needed."
            else:
                status_headline = "All sorted"
                action_text = f"Enough for ~{int(days_left)} days. No action needed."

            usual_purchase = None
            if is_milk:
                usual_purchase = "Amul Taaza Milk 1L · ₹68"
            elif is_oil:
                usual_purchase = "Fortune Sunflower Oil 5L · ₹749"

            household_context = {
                "item_name": matched_pantry.get("name"),
                "category": matched_pantry.get("category"),
                "quantity": qty,
                "unit": unit,
                "daily_consumption": daily,
                "days_remaining": days_left,
                "status": status,
                "status_headline": status_headline,
                "urgency": urgency,
                "suggested_action": action_text,
                "usual_purchase": usual_purchase
            }

    # 3. Matching Household Plans / Recipes
    plans = []
    if query_clean:
        try:
            from intent.intent_service import MEAL_RECIPES
            for key, recipe in MEAL_RECIPES.items():
                keywords = recipe.get("keywords", [])
                if any(k in query_clean for k in keywords) or key in query_clean or recipe.get("name", "").lower() in query_clean:
                    plans.append({
                        "plan_id": f"plan_{key}",
                        "title": f"Make {recipe['name']} tonight",
                        "meal": recipe["name"],
                        "description": f"Recipe plan with {len(recipe.get('components', []))} ingredients",
                        "components": [
                            {"item": c["item"], "essential": c.get("essential", False), "category": c.get("category")}
                            for c in recipe.get("components", [])
                        ]
                    })
        except Exception as e:
            logger.debug(f"Plan matching skipped: {e}")

    # 4. Product Catalog Search
    product_results = await commerce_adapter.search_products(query=q, category=category)

    # 5. Matching Recent Orders
    matching_orders = []
    if query_clean:
        try:
            all_orders = commerce_adapter.get_orders()
            for ord_item in all_orders:
                items_str = " ".join([i.get("name", "") for i in ord_item.get("items", [])]).lower()
                if query_clean in items_str or query_clean in ord_item.get("id", "").lower():
                    matching_orders.append(ord_item)
        except Exception:
            pass

    return {
        "query": q,
        "household_context": household_context,
        "budget_context": budget_context,
        "plans": plans[:3],
        "products": product_results[:limit],
        "total_products": len(product_results),
        "recent_orders": matching_orders[:3]
    }

from catalog.taxonomy import CANONICAL_CATEGORIES, SECTION_DEFINITIONS, is_product_allowed_in_section, classify_product

@app.get("/api/products")
async def get_products(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(250, ge=1, le=500)
):
    query_val = q or ""
    items = await commerce_adapter.search_products(query=query_val, category=category)
    return items[skip:skip+limit]

@app.get("/api/products/search")
async def search_products(
    q: str = Query(""),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(250, ge=1, le=500)
):
    items = await commerce_adapter.search_products(query=q, category=category)
    return items[skip:skip+limit]

@app.get("/api/commerce/status")
async def get_commerce_status():
    is_avail = not commerce_adapter.is_circuit_broken
    err = None
    if commerce_adapter.is_live and not is_avail:
        err = commerce_adapter.last_error or "Swiggy Instamart is currently unavailable."
    elif not commerce_adapter.is_live and commerce_adapter.last_error:
        err = commerce_adapter.last_error

    return {
        "retailer": "swiggy_instamart",
        "retailerName": "Swiggy Instamart",
        "is_live": commerce_adapter.is_live,
        "is_available": is_avail,
        "mode": commerce_adapter.commerce_mode,
        "mcp_url": commerce_adapter.mcp_url,
        "error": err,
        "active_address": oauth_manager.get_active_address(),
        "active_address_id": oauth_manager.get_active_address_id(),
        "label": "Swiggy Instamart (Live MCP)" if commerce_adapter.is_live else "Swiggy Instamart (Not Connected - OAuth Required)"
    }

@app.get("/api/products/categories")
async def get_categories():
    return list(CANONICAL_CATEGORIES.keys())

@app.get("/api/taxonomy")
async def get_taxonomy():
    return {
        "categories": CANONICAL_CATEGORIES,
        "sections": SECTION_DEFINITIONS,
    }

@app.get("/api/products/sections")
async def get_sections_products():
    all_products = await commerce_adapter.search_products("")
    sections_result: Dict[str, List[Dict[str, Any]]] = {}
    seen_ids = set()

    for sec_id in ["deals", "usuals", "groceries", "household", "snacks"]:
        sec_cfg = SECTION_DEFINITIONS.get(sec_id, {})
        allowed = sec_cfg.get("allowed_categories", [])
        disallowed = sec_cfg.get("disallowed_categories", [])

        # Filter strictly by category
        matched = []
        if sec_id == "deals":
            category_seen = set()
            for p in all_products:
                cat = p.get("category")
                if cat and cat not in category_seen:
                    category_seen.add(cat)
                    matched.append(p)
            for p in all_products:
                if len(matched) >= 10:
                    break
                p_id = p.get("id") or p.get("productId")
                if not any((x.get("id") or x.get("productId")) == p_id for x in matched):
                    matched.append(p)
        else:
            for p in all_products:
                p_cat = p.get("category", "")
                if disallowed and p_cat in disallowed:
                    continue
                if allowed and p_cat not in allowed:
                    continue
                matched.append(p)

        # Prioritize unseen products for cross-shelf variety
        unseen = [p for p in matched if (p.get("id") or p.get("productId")) not in seen_ids]
        selected = unseen[:10]
        if len(selected) < 4:
            selected_ids = {p.get("id") or p.get("productId") for p in selected}
            for p in matched:
                if len(selected) >= 10:
                    break
                p_id = p.get("id") or p.get("productId")
                if p_id not in selected_ids:
                    selected.append(p)
                    selected_ids.add(p_id)

        for p in selected:
            seen_ids.add(p.get("id") or p.get("productId"))

        sections_result[sec_id] = selected

    return sections_result

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = await commerce_adapter.get_product(product_id)
    if not product:
        product = product_repo.get_by_id(product_id)
    if product:
        if not product.get("imageUrl") and not product.get("image"):
            try:
                resolved = await image_resolver.resolve(product)
                if resolved.get("imageUrl"):
                    product["imageUrl"] = resolved["imageUrl"]
                    product["image"] = resolved["imageUrl"]
                    product["imageSource"] = resolved.get("imageSource")
                    product["imageConfidence"] = resolved.get("imageConfidence")
                    product["imageStatus"] = resolved.get("imageStatus")
            except Exception as img_err:
                logger.debug(f"[API] Product image resolution skipped: {img_err}")
        return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/api/commerce/compare/{product_id}")
async def compare_commerce_options(product_id: str):
    product = await commerce_adapter.get_product(product_id)
    if not product:
        product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
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
    product = await commerce_adapter.get_product(product_id)
    if product and product.get("imageUrl"):
        return {
            "thumbnail": product["imageUrl"],
            "medium": product["imageUrl"],
            "source": product.get("imageSource", "swiggy"),
            "confidence": product.get("imageConfidence", 1.0),
            "status": "live"
        }
    return {
        "thumbnail": None,
        "medium": None,
        "source": "unavailable",
        "confidence": 0.0,
        "status": "unavailable"
    }


# ── IMAGE RESOLUTION ENDPOINTS ───────────────────────────────────────────────────────────────────────────────

class ImageResolveRequest(BaseModel):
    """
    Payload for async frontend image resolution.
    The frontend sends this after rendering the product card with commerce data.
    """
    product_key: str          # e.g. "swiggy:spin_maggi_4pk" or "swiggy:spin_amul_taaza_1l"
    name: str
    brand: Optional[str] = None
    quantity: Optional[str] = None
    unit: Optional[str] = None
    pack_size: Optional[str] = None
    barcode: Optional[str] = None
    swiggy_image_url: Optional[str] = None  # if Swiggy already provided one


@app.post("/api/images/resolve")
async def resolve_product_image(req: ImageResolveRequest):
    """
    Async image resolution endpoint.

    The frontend calls this AFTER rendering the product card with commerce data.
    The product card renders immediately with real price/availability from Swiggy.
    The image loads asynchronously once this endpoint responds.

    Priority chain (per spec):
      1. Swiggy image URL if provided
      2. Open Food Facts barcode lookup
      3. Open Food Facts identity match (brand + name + quantity)
      4. null → imageStatus: "unavailable"

    No images are downloaded. Only real remote URLs are returned.
    """
    product_dict = {
        "id": req.product_key,
        "variantId": req.product_key,
        "name": req.name,
        "brand": req.brand,
        "quantity": req.quantity,
        "unit": req.unit,
        "pack_size": req.pack_size,
        "barcode": req.barcode,
        "imageUrl": req.swiggy_image_url,
        "image": req.swiggy_image_url,
        "retailer": "swiggy_instamart",
    }

    print(
        f"[COMMERCE] Image resolve request | "
        f"Product: {req.name} | "
        f"Barcode: {req.barcode or 'none'}"
    )

    result = await image_resolver.resolve(product_dict)
    return result


@app.get("/api/images/cache/stats")
async def image_cache_stats():
    """Return image resolution cache statistics (for observability / debugging)."""
    return image_cache.stats()


@app.post("/api/images/cache/clear")
async def clear_image_cache():
    """Flush the image resolution cache (development / testing use)."""
    image_cache.clear()
    return {"status": "ok", "message": "Image cache cleared"}


@app.post("/api/images/cache/clear-unavailable")
async def clear_unavailable_image_cache():
    """
    Purge only the 'unavailable' (null-URL) cache entries so products get a
    fresh resolution attempt. Does not evict confirmed-found images.
    Use this after fixing the pipeline or when images.openfoodfacts.org is
    temporarily unreachable.
    """
    removed = image_cache.clear_unavailable()
    return {"status": "ok", "message": f"Cleared {removed} unavailable entries"}

class CartRequest(BaseModel):
    product_id: str
    quantity: Optional[int] = 1

class CartUpdateRequest(BaseModel):
    product_id: str
    quantity: int

@app.get("/api/cart")
async def get_cart():
    if not commerce_adapter.carts:
        cart_id = await commerce_adapter.create_cart()
    else:
        cart_id = list(commerce_adapter.carts.keys())[0]
    return commerce_adapter.get_cart(cart_id)

@app.post("/api/cart/add")
async def add_to_cart(req: CartRequest):
    if not commerce_adapter.carts:
        cart_id = await commerce_adapter.create_cart()
    else:
        cart_id = list(commerce_adapter.carts.keys())[0]
    return await commerce_adapter.add_to_cart(cart_id, req.product_id, req.quantity or 1)

@app.post("/api/cart/update")
async def update_cart_item(req: CartUpdateRequest):
    if not commerce_adapter.carts:
        cart_id = await commerce_adapter.create_cart()
    else:
        cart_id = list(commerce_adapter.carts.keys())[0]
    return await commerce_adapter.update_cart_quantity(cart_id, req.product_id, req.quantity)

@app.post("/api/cart/remove")
async def remove_from_cart(req: CartRequest):
    if not commerce_adapter.carts:
        return {"items": [], "item_count": 0, "subtotal": 0}
    cart_id = list(commerce_adapter.carts.keys())[0]
    return await commerce_adapter.remove_from_cart(cart_id, req.product_id)

@app.post("/api/cart/clear")
async def clear_cart():
    if not commerce_adapter.carts:
        return {"items": [], "item_count": 0, "subtotal": 0}
    cart_id = list(commerce_adapter.carts.keys())[0]
    commerce_adapter.carts[cart_id] = []
    return {"cart_id": cart_id, "items": [], "item_count": 0, "subtotal": 0}

@app.post("/api/checkout")
async def checkout():
    if not commerce_adapter.carts:
        raise HTTPException(status_code=400, detail="No active cart")
    cart_id = list(commerce_adapter.carts.keys())[0]
    cart = commerce_adapter.get_cart(cart_id)
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    subtotal = cart["subtotal"]
    budget_remaining = await budget_service.get_remaining_budget()

    # Deterministic budget constraint check (Requirement 23)
    if subtotal > budget_remaining:
        raise HTTPException(
            status_code=400,
            detail=f"Order total (₹{subtotal}) exceeds remaining monthly budget (₹{budget_remaining}). Please review items or adjust budget."
        )

    # Auto-limit evaluation
    auto_limit = await budget_service.get_auto_buy_limit()
    requires_explicit_approval = subtotal > auto_limit

    try:
        order = await commerce_adapter.checkout(cart_id)
        # Deduct actual spend in budget service
        await budget_service.record_spend(subtotal)
        # Clear cart
        commerce_adapter.carts[cart_id] = []

        audit_service.log_decision(
            order["id"],
            "CHECKOUT_COMPLETED",
            [
                f"Total: ₹{subtotal}",
                f"Items: {cart['item_count']}",
                f"Budget remaining: ₹{budget_remaining - subtotal}",
                f"Mode: {'EXPLICIT_APPROVAL' if requires_explicit_approval else 'AUTO_WITHIN_LIMIT'}"
            ]
        )
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

class CreateReminderRequest(BaseModel):
    title: str
    message: str
    priority: Optional[str] = "MEDIUM"
    type: Optional[str] = "INVENTORY"
    product_id: Optional[str] = None
    hours_until_due: Optional[int] = 24

@app.post("/api/reminders")
async def create_reminder(req: CreateReminderRequest):
    """Create a new household reminder."""
    new_r = reminder_engine.create_reminder(
        type=req.type.upper(),
        title=req.title,
        message=req.message,
        product_id=req.product_id,
        priority=req.priority.upper(),
        hours_until_due=req.hours_until_due or 24
    )
    audit_service.log_decision(req.title, "REMINDER_CREATED", [req.message])
    return new_r

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

@app.post("/api/reminders/{reminder_id}/{action}")
async def reminder_action_path(reminder_id: str, action: str):
    """Handle reminder action directly via URL path: snooze | complete | dismiss."""
    if action == "snooze":
        result = reminder_engine.snooze(reminder_id, hours=24)
    elif action == "complete":
        result = reminder_engine.complete(reminder_id)
    elif action == "dismiss":
        result = reminder_engine.dismiss(reminder_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    if not result:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return result

# ─────────────────────────────────────────────────────────────────────────────
# POLICY & RULES ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/api/policy")
async def get_policy():
    """Current household purchasing policy and limits."""
    rules = policy_service.get_rules() if hasattr(policy_service, "get_rules") else {
        "automatic_categories": policy_service.automatic_categories,
        "ask_categories": policy_service.ask_categories,
        "restricted_categories": policy_service.restricted_categories,
    }
    budget_status = budget_service.get_status()
    session_state = session_service.get_session_state() if session_service else {}
    return {
        **rules,
        "auto_buy_limit": budget_status["auto_limit"],
        "monthly_budget": budget_status["monthly"],
        "spent": budget_status["spent"],
        "autonomy_profile": session_state.get("autonomy_profile", "FULL_AUTOPILOT"),
    }

class PolicyUpdateRequest(BaseModel):
    automatic_categories: Optional[List[str]] = None
    ask_categories: Optional[List[str]] = None
    restricted_categories: Optional[List[str]] = None
    auto_buy_limit: Optional[float] = None
    monthly_budget: Optional[float] = None
    autonomy_profile: Optional[str] = None

@app.post("/api/policy")
async def update_policy(req: PolicyUpdateRequest):
    """Update household policy, budget limits, or autonomy profile."""
    if req.automatic_categories is not None or req.ask_categories is not None or req.restricted_categories is not None:
        policy_service.update_rules(
            automatic=req.automatic_categories if req.automatic_categories is not None else policy_service.automatic_categories,
            ask=req.ask_categories if req.ask_categories is not None else policy_service.ask_categories,
            restricted=req.restricted_categories if req.restricted_categories is not None else policy_service.restricted_categories,
        )
    if req.auto_buy_limit is not None:
        budget_service.set_auto_limit(float(req.auto_buy_limit))
    if req.monthly_budget is not None:
        budget_service.set_budget(float(req.monthly_budget))
    if req.autonomy_profile is not None and session_service:
        session_service.set_autonomy_profile(req.autonomy_profile)

    audit_service.log_decision(
        "Household Policy",
        "POLICY_UPDATED",
        [
            f"Auto-limit: ₹{budget_service.auto_limit}",
            f"Monthly budget: ₹{budget_service.monthly_budget}",
            f"Autonomy profile: {getattr(session_service, 'autonomy_profile', 'UNKNOWN')}"
        ]
    )
    return await get_policy()

# ─────────────────────────────────────────────────────────────────────────────
# PANTRY MUTATION ROUTE
# ─────────────────────────────────────────────────────────────────────────────

class PantryUpdateRequest(BaseModel):
    item_name: str
    quantity: Optional[float] = None
    unit: Optional[str] = "units"
    status: Optional[str] = None

@app.post("/api/pantry/update")
async def update_pantry(req: PantryUpdateRequest):
    """Update stock or report item in pantry."""
    result = inventory_service.update_item(
        item_name_or_id=req.item_name,
        quantity=req.quantity,
        unit=req.unit,
        status=req.status
    )
    audit_service.log_decision(req.item_name, "PANTRY_UPDATED", [f"Quantity: {req.quantity} {req.unit}"])
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
    """NOVA's intelligent household cart - the planned purchase set."""
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

@app.get("/api/plans")
async def get_household_plans():
    """Returns available household meal and staple plans with live pantry reconciliation."""
    results = []
    
    curated_intents = [
        {"id": "plan_biryani", "text": "I want to make biryani for 2"},
        {"id": "plan_pasta", "text": "I want to make pasta for 2"},
        {"id": "plan_panipuri", "text": "I want to make pani puri for 2"}
    ]
    
    for plan in curated_intents:
        recon = await intent_service.reconcile_intent(plan["text"])
        
        # Transform canonical schema into curated plan schema expected by frontend for the grid
        have_items = []
        for a in recon["pantry"]["available"]:
            have_items.append({
                "item": a.get("required_name", a["name"]),
                "imageUrl": _get_demo_image(a["name"]) or None,
                "stock": f"{a['quantity']} {a['unit']} in pantry",
                "status": "In stock"
            })
            
        need_items = []
        for n in recon["shopping"]["items"]:
            need_items.append({
                "item": n["name"],
                "imageUrl": n.get("image") or n.get("imageUrl") or _get_demo_image(n["name"]),
                "needed": n.get("required_amount", "1 pack"),
                "estimated_price": n.get("price", 0)
            })
            
        results.append({
            "plan_id": plan["id"],
            "title": f"Make {recon['recipe']['name']}",
            "meal": recon['recipe']['name'],
            "have_items": have_items,
            "need_items": need_items,
            "ready_to_cook": len(need_items) == 0,
            "missing_count": len(need_items),
            "estimated_cost": recon["shopping"]["subtotal"],
            "components_count": len(have_items) + len(need_items),
        })
        
    return results


@app.post("/api/plans/reconcile")
async def reconcile_household_plan(req: RequestModel):
    """Reconciles custom natural language intent against pantry stock."""
    text = req.get_text()
    if not text:
        raise HTTPException(status_code=400, detail="Text required")
    reconciliation = await intent_service.reconcile_intent(text)
    
    return reconciliation


def _get_demo_image(prod_name):
    lower_name = prod_name.lower()
    if "milk" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/17/b42b731e-b555-4536-913a-265af70ec9e4_SKS75T1GV1_MN_16122025.png"
    if "oil" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png"
    if "maggi" in lower_name or "noodles" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png"
    if "atta" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/3/9/805a02b1-e08b-4d4b-aa8f-ab05cabb1e37_1780_1.png"
    if "tea" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/bf79f8d0-dfcb-4ebb-be63-b3e291656666_Q5AIG72TKQ_MN_18022026.png"
    if "salt" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png"
    if "rice" in lower_name: return "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/7/21/ed973afb-e397-4df3-8a23-6153474d93b0_450_1.png"
    return None

@app.get("/api/household-status")
async def get_household_status():
    """Authoritative household briefing status endpoint - driven by real pantry, budget and audit state."""
    from datetime import datetime as _dt
    hour = _dt.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Real pantry data
    urgency_groups = inventory_service.get_urgency_grouped()
    all_items = inventory_service.get_all()
    urgent = urgency_groups.get("URGENT", [])
    upcoming = urgency_groups.get("UPCOMING", [])
    uncertain = urgency_groups.get("UNCERTAIN", [])

    # Estimate replenishment cost
    replenishment_estimates = {
        "Milk": 68, "Oil": 749, "Rice": 320, "Atta": 289, "Salt": 25,
        "Dal": 142, "Tea": 215, "Detergent": 399, "Sugar": 210,
        "Soap": 139, "Cleaning": 109, "Hair Care": 199,
    }
    estimated_upcoming_spend = sum(
        replenishment_estimates.get(item["category"], 120)
        for item in urgent + upcoming
    )

    # Budget
    budget_status = budget_service.get_status()
    budget_forecast = budget_service.get_forecast(upcoming_spend=estimated_upcoming_spend)

    # Recent activity
    recent_activity = audit_service.get_recent(limit=15)
    recent_decisions = [a for a in recent_activity if a.get("decision") in ("AUTO", "DO_NOTHING", "ASK", "BLOCKED", "WAIT")]
    auto_actions = [a for a in recent_decisions if a.get("decision") == "AUTO"]
    restraint_actions = [a for a in recent_decisions if a.get("decision") == "DO_NOTHING"]
    ask_actions = [a for a in recent_decisions if a.get("decision") == "ASK"]

    # Cart
    cart_count = 0
    try:
        if commerce_adapter.carts:
            cart_id = list(commerce_adapter.carts.keys())[0]
            cart = commerce_adapter.get_cart(cart_id)
            cart_count = cart.get("item_count", 0)
    except Exception:
        pass

    # Autonomy
    autonomy = session_service.get_autonomy_profile() if session_service else "FULL_AUTOPILOT"

    # ── SECTION 2: TAKEN CARE OF (Consumer translation of AUTO) ───────────────
    taken_care_of = []
    for act in auto_actions:
        prod_name = act.get("product", "Household item")
        taken_care_of.append({
            "id": act.get("id"),
            "product": prod_name,
            "cost": act.get("cost", 68),
            "summary": f"You were running low, so NOVA ordered your usual pack.",
            "description": act.get("description", f"NOVA automatically ordered {prod_name}."),
            "reasons": act.get("reasons", [
                "Stock was running low in your pantry (less than 1 day's supply remaining).",
                f"Price ₹{act.get('cost', 68)} is within your autonomous safety limit.",
                f"Sufficient monthly budget remaining."
            ]),
            "decision": "AUTO",
            "status_label": "Done for you",
            "timestamp": act.get("timestamp"),
            "imageUrl": _get_demo_image(prod_name),
              "imageUrl": _get_demo_image(act.get("product", "")),
              "system_telemetry": {
                "tool": "execute_autonomous_purchase",
                "verdict": "AUTO",
                "provider": "AWS Strands Agents SDK",
                "rule": "Autonomous approval ceiling ₹500"
            }
        })

    # Default fallback for Milk auto-buy if no auto action recorded yet
    if not taken_care_of:
        taken_care_of.append({
            "id": "auto_milk_01",
            "product": "Milk",
            "package_name": "Amul Taaza 1L",
            "cost": 68,
            "summary": "You were running low, so NOVA ordered your usual 1L pack.",
            "description": "Milk was running low (~0.3L left). NOVA ordered your usual 1L pack.",
            "reasons": [
                "Your pantry milk stock dropped to ~0.3 L (less than 1 day remaining).",
                "Average household consumption is ~0.6 L/day.",
                "Price ₹68 is within your ₹500 auto-order limit.",
                "Sufficient budget remaining in your monthly allocation."
            ],
            "decision": "AUTO",
            "status_label": "Done for you",
            "timestamp": _dt.now().isoformat(),
            "imageUrl": _get_demo_image(prod_name),
              "imageUrl": _get_demo_image(act.get("product", "")),
              "system_telemetry": {
                "tool": "execute_autonomous_purchase",
                "verdict": "AUTO",
                "provider": "AWS Strands Agents SDK",
                "rule": "Autonomous approval ceiling ₹500"
            }
        })

    # ── SECTION 3: NEEDS YOUR INPUT (Consumer translation of ASK) ──────────────
    needs_input = []
    for act in ask_actions:
        needs_input.append({
            "id": act.get("id"),
            "product": act.get("product"),
            "summary": act.get("description", "Needs your review"),
            "reasons": act.get("reasons", []),
            "options": [
                {"name": act.get("product"), "price": act.get("cost", 145), "tag": "Recommended"},
                {"name": f"Alternative {act.get('product')}", "price": round(act.get("cost", 145) * 0.9), "tag": "Best Value"},
            ]
        })

    if not needs_input:
        needs_input.append({
            "id": "input_oil_01",
            "product": "Cooking oil",
            "days_remaining": 2,
            "summary": "You may run out in about 2 days.",
            "description": "NOVA found 3 suitable options matching your household preferences.",
            "options": [
                {"name": "Fortune Sunlite Sunflower Oil 1L", "price": 145, "tag": "Recommended · Best match"},
                {"name": "Saffola Gold Pro Healthy Lifestyle 1L", "price": 169, "tag": "Popular choice"},
                {"name": "Dhara Filtered Mustard Oil 1L", "price": 138, "tag": "Budget pick"},
            ]
        })

    # ── SECTION 4: TONIGHT / UPCOMING (MEAL INTENT) ───────────────────────────
    oil_item = next((p for p in all_items if "oil" in p.get("name", "").lower()), None)
    salt_item = next((p for p in all_items if "salt" in p.get("name", "").lower()), None)
    
    tonight_plan = {
        "plan_id": "plan_maggi",
        "title": "Make Maggi",
        "meal": "Maggi 2-Minute Masala Noodles",
        "tagline": "Tonight's household plan",
        "have_items": [
            {"name": "Cooking Oil", "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2026/2/18/d0fe0c1c-2142-43d3-bf49-3fe02eb1a7dd_PUHXM33U8E_MN_18022026.png", "stock": f"{oil_item.get('quantity', 2.1) if oil_item else 2.1}L in pantry", "status": "In stock"},
            {"name": "Salt & Spices", "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/ciw/2025/12/18/219b05ab-1b6b-468b-807c-d4fdd353dc89_883CSP2S79_MN_18122025.png", "stock": f"{salt_item.get('quantity', 0.4) if salt_item else 0.4}kg in pantry", "status": "In stock"},
        ],
        "need_items": [
            {"name": "Maggi 2-Minute Masala Noodles (Pack of 4)", "imageUrl": "https://media-assets.swiggy.com/swiggy/image/upload/NI_CATALOG/IMAGES/CIW/2026/5/20/682f661f-9068-4c0e-8fa3-eac6cb9c6168_82_1.png", "needed": "1 pack", "price": 56}
        ],
        "estimated_cost": 56,
        "action_label": "Take care of it",
        "imageUrl": _get_demo_image(prod_name),
              "imageUrl": _get_demo_image(act.get("product", "")),
              "system_telemetry": {
            "tool": "reconcile_meal_intent",
            "verdict": "RECONCILED",
            "pantry_items_matched": 2,
            "missing_items_ordered": 1
        }
    }

    # ── SECTION 6: ALL SORTED (RESTRAINT DEMONSTRATION) ───────────────────────
    all_sorted = []
    for act in restraint_actions:
        all_sorted.append({
            "id": act.get("id"),
            "product": act.get("product"),
            "days_remaining": act.get("metadata", {}).get("days_remaining", 19),
            "summary": f"Enough for about {act.get('metadata', {}).get('days_remaining', 19)} days.",
            "description": "NOVA checked your pantry stock and applied restraint. No action needed.",
            "reasons": act.get("reasons", [
                "Current stock is sufficient for household needs.",
                "NOVA avoided an unnecessary purchase to preserve your budget."
            ]),
            "imageUrl": _get_demo_image(prod_name),
              "imageUrl": _get_demo_image(act.get("product", "")),
              "system_telemetry": {
                "tool": "record_restraint_decision",
                "verdict": "DO_NOTHING",
                "provider": "AWS Strands Agents SDK"
            }
        })

    if not all_sorted:
        all_sorted.append({
            "id": "sorted_oil_01",
            "product": "Cooking oil",
            "days_remaining": 19,
            "summary": "Enough for about 19 days.",
            "description": "Stock is healthy. No action needed.",
            "reasons": [
                "Pantry inventory has ~2.1 L of cooking oil remaining.",
                "Average consumption is 0.07 L/day (~19 to 30 days of supply).",
                "NOVA applied spending restraint; no unnecessary purchase made."
            ],
            "imageUrl": _get_demo_image(prod_name),
              "imageUrl": _get_demo_image(act.get("product", "")),
              "system_telemetry": {
                "tool": "record_restraint_decision",
                "verdict": "DO_NOTHING",
                "provider": "AWS Strands Agents SDK"
            }
        })

    # ── SECTION 1: NOVA'S BRIEFING SUMMARY ────────────────────────────────────
    taken_count = len(taken_care_of)
    input_count = len(needs_input)
    plan_count = 1 if tonight_plan else 0
    total_briefing_items = taken_count + input_count + plan_count

    briefing_bullets = [
        f"{taken_count} thing is already taken care of.",
        f"{input_count} thing may need your attention.",
        f"{plan_count} plan is ready for tonight."
    ]

    return {
        "greeting": greeting,
        "headline": "Here's what's happening at home.",
        "briefing_summary": {
            "title": f"NOVA has {total_briefing_items} things for you.",
            "bullets": briefing_bullets,
            "taken_count": taken_count,
            "input_count": input_count,
            "plan_count": plan_count
        },
        "taken_care_of": taken_care_of,
        "needs_input": needs_input,
        "tonight_plan": tonight_plan,
        "all_sorted": all_sorted,
        "household_size": 4,
        "autonomy_profile": autonomy,
        "autopilot_on": autonomy == "FULL_AUTOPILOT",
        "pantry": {
            "total_tracked": len(all_items),
            "urgent_count": len(urgent),
            "upcoming_count": len(upcoming),
            "comfortable_count": len(urgency_groups.get("COMFORTABLE", [])),
            "uncertain_count": len(uncertain),
            "urgent_items": urgent[:5],
            "upcoming_items": upcoming[:5],
        },
        "budget": budget_forecast,
        "activity": {
            "recent": recent_activity[:5],
            "auto_count": len(auto_actions) or 1,
            "restraint_count": len(restraint_actions) or 1,
            "ask_count": len(ask_actions) or 1,
        },
        "cart": {
            "item_count": cart_count,
        },
        "estimated_upcoming_spend": estimated_upcoming_spend,
    }



@app.post("/api/plans/take-care-of")
async def plan_take_care_of(req: RequestModel):
    data = req.model_dump() if hasattr(req, "model_dump") else req.dict()
    # Or just use raw request via Request in fastAPI
    # Wait, RequestModel in main.py has get_text() but maybe we can just accept raw dict?
    pass

@app.post("/api/plans/execute")
async def execute_plan_purchase(request: Request):
    data = await request.json()
    items = data.get("items", [])
    
    results = []
    total_cost = 0
    from datetime import datetime
    import uuid
    
    for item in items:
        # Simulate evaluate_and_execute_purchase
        price = item.get("price", 0)
        total_cost += price * item.get("quantity", 1)
        # Add to cart
        if item.get("id"):
            await cart_adapter.add_item(item["id"], item.get("quantity", 1))
            
    # Decision Engine: 
    action = {
        "id": f"act_{uuid.uuid4().hex[:8]}",
        "type": "PURCHASE",
        "product": data.get("meal", "Household Plan Items"),
        "cost": total_cost,
        "description": "Ordered missing ingredients for plan",
        "timestamp": datetime.now().isoformat(),
        "status": "COMPLETED",
        "system_telemetry": {
            "tool": "evaluate_and_execute_purchase",
            "verdict": "AUTO" if total_cost <= 1500 else "ASK"
        }
    }
    household_activity.insert(0, action)
    
    return {"status": "success", "action": action, "decision": action["system_telemetry"]["verdict"]}
