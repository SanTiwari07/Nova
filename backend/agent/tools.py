"""
Nova Agent Tool Registry for AWS Strands Agents SDK.
Exposes existing backend services as real Strands tools with full type annotations and OpenAPI docstrings.
"""
from typing import Dict, Any, List, Optional
from strands import tool

try:
    from intent.intent_service import IntentReconciliationService
except ImportError:
    from backend.intent.intent_service import IntentReconciliationService

def create_nova_tools(
    inventory_service,
    budget_service,
    policy_service,
    commerce_adapter,
    history_service,
    decision_engine,
    audit_service,
    session_service=None,
    reminder_engine=None,
    savings_engine=None,
    intent_service=None
) -> list:
    """
    Creates and returns the suite of Strands Agent tools wired to the application's services.
    """
    reconciliation_service = intent_service or IntentReconciliationService(inventory_service=inventory_service)

    @tool
    def get_pantry_inventory(category: str = "") -> Dict[str, Any]:
        """
        Check current household pantry stock and inventory levels.
        Returns list of items with their current quantity, unit, days of supply remaining,
        and replenishment status ('LOW' vs 'HEALTHY').
        
        Args:
            category: Optional category filter (e.g. 'Milk', 'Rice', 'Atta', 'Oil', 'Detergent').
        """
        all_items = inventory_service.get_all()
        if category:
            cat_lower = category.lower()
            filtered = [
                i for i in all_items 
                if cat_lower in i.get("category", "").lower() or cat_lower in i.get("name", "").lower()
            ]
        else:
            filtered = all_items

        low_stock = [i for i in filtered if i.get("status") == "LOW"]
        return {
            "total_items_checked": len(filtered),
            "items": filtered,
            "low_stock_items": [i["name"] for i in low_stock],
            "low_stock_count": len(low_stock)
        }

    @tool
    def get_purchase_history(category: str = "") -> Dict[str, Any]:
        """
        Retrieve recurring household items from purchase history.
        Shows typical purchase intervals, usual order quantities, historical average prices,
        current prices, and days until replenishment is typically needed.
        
        Args:
            category: Optional category filter.
        """
        history = history_service.get_recurring_products()
        if category:
            cat_lower = category.lower()
            history = [
                h for h in history 
                if cat_lower in h.get("category", "").lower() or cat_lower in h.get("name", "").lower()
            ]
        
        due_soon = [h for h in history if h.get("days_until_needed", 30) <= 7]
        return {
            "source": "AMAZON_MOCK",
            "recurring_count": len(history),
            "due_soon_count": len(due_soon),
            "items_due_soon": [
                {
                    "name": h["name"],
                    "days_until_needed": h.get("days_until_needed"),
                    "avg_price": h.get("avg_price"),
                    "typical_quantity": h.get("typical_quantity", 1),
                    "confidence": h.get("confidence", 0.9)
                }
                for h in due_soon
            ],
            "all_recurring_products": [
                {
                    "product_id": h["product_id"],
                    "name": h["name"],
                    "category": h["category"],
                    "typical_interval_days": h.get("typical_interval_days"),
                    "days_until_needed": h.get("days_until_needed"),
                    "current_price": h.get("current_price"),
                    "avg_price": h.get("avg_price")
                }
                for h in history
            ]
        }

    @tool
    def get_household_overview() -> Dict[str, Any]:
        """
        Retrieve high-level overview of the household state: budget remaining, items running low,
        active reminders, and potential savings opportunities.
        """
        recurring = history_service.get_recurring_products() if history_service else []
        due_soon = [p for p in recurring if p.get("days_until_needed", 30) <= 7]
        pantry = inventory_service.get_all()
        low_pantry = [p for p in pantry if p.get("status") == "LOW"]
        
        active_reminders = reminder_engine.get_reminders(status="ACTIVE") if reminder_engine else []
        savings = savings_engine.get_savings_opportunities() if savings_engine else {"total_potential_saving": 0}
        
        return {
            "budget_remaining": budget_service.monthly_budget - budget_service.spent,
            "monthly_budget": budget_service.monthly_budget,
            "spent_so_far": budget_service.spent,
            "auto_buy_limit": budget_service.auto_limit,
            "pantry_low_items_count": len(low_pantry),
            "items_due_soon_count": len(due_soon),
            "active_reminders_count": len(active_reminders),
            "potential_monthly_savings": savings.get("total_potential_saving", 0),
            "autonomy_profile": getattr(session_service, "autonomy_profile", "NONE")
        }

    @tool
    def get_budget_status() -> Dict[str, Any]:
        """
        Check current household budget numbers: monthly budget, spend so far,
        remaining budget, and single-item auto-buy limit.
        """
        remaining = budget_service.monthly_budget - budget_service.spent
        return {
            "monthly_budget": budget_service.monthly_budget,
            "spent": budget_service.spent,
            "remaining_budget": remaining,
            "auto_buy_limit": budget_service.auto_limit,
            "auto_buy_permitted": remaining > 0
        }

    @tool
    def check_category_policy(category: str) -> Dict[str, Any]:
        """
        Check safety policies and autonomy rules for a product category.
        Reveals if a category is automatic (allowed for autonomous ordering),
        requires explicit user approval (ASK), or is restricted/blocked.
        
        Args:
            category: The product category name (e.g. 'Milk', 'Rice', 'Snacks', 'Electronics', 'Alcohol').
        """
        cat_lower = category.lower() if category else ""
        is_restricted = any(r.lower() in cat_lower for r in policy_service.restricted_categories)
        requires_ask = any(a.lower() in cat_lower for a in policy_service.ask_categories)
        is_auto = any(a.lower() in cat_lower for a in policy_service.automatic_categories)

        status = "RESTRICTED" if is_restricted else "REQUIRES_APPROVAL" if requires_ask else "AUTOMATIC" if is_auto else "STANDARD"
        return {
            "category": category,
            "policy_status": status,
            "is_allowed": not is_restricted,
            "requires_user_approval": requires_ask or not is_auto,
            "is_automatic": is_auto and not is_restricted
        }

    @tool
    async def search_catalog(query: str, category: str = "") -> List[Dict[str, Any]]:
        """
        Search catalog / Swiggy Instamart for available grocery and household products.
        Returns product ID, name, brand, pack size, price, and stock availability.
        
        Args:
            query: Product name or keyword (e.g. 'milk', 'maggi noodles', 'surf excel', 'atta').
            category: Optional category filter.
        """
        filters = {"category": category} if category else None
        try:
            results = await commerce_adapter.search_products(query=query, category=category, filters=filters)
        except Exception:
            try:
                results = await commerce_adapter.search_products(query=query)
            except Exception as e:
                return [{"error": str(e)}]

        if not results:
            return []

        compact_results = []
        for p in results[:8]:
            compact_results.append({
                "product_id": p.get("id") or p.get("productId"),
                "name": p.get("name"),
                "brand": p.get("brand"),
                "pack_size": p.get("pack_size") or p.get("packSize") or p.get("unit"),
                "price": p.get("price") or p.get("productPrice"),
                "category": p.get("category"),
                "availability": p.get("availability", "IN_STOCK"),
                "delivery_estimate": p.get("deliveryEstimate", "10-15 min")
            })
        return compact_results

    @tool
    async def compare_product_offers(product_id: str) -> Dict[str, Any]:
        """
        Compare retailer offers and prices across Amazon, Swiggy Instamart, Zepto, and Blinkit
        for a specific product ID.
        
        Args:
            product_id: The ID of the product to compare (e.g. 'prod_000109' or 'swiggy:spin_maggi_4pk').
        """
        offers = await commerce_adapter.compare_options(product_id)
        valid_offers = [o for o in offers if o.get("availability") == "IN_STOCK"]
        best_offer = min(valid_offers, key=lambda x: x.get("effectiveTotal", 9999)) if valid_offers else None
        
        return {
            "product_id": product_id,
            "available_retailers": len(valid_offers),
            "best_offer": {
                "retailer": best_offer.get("retailerName"),
                "effective_total": best_offer.get("effectiveTotal"),
                "delivery_estimate": best_offer.get("deliveryEstimate")
            } if best_offer else None,
            "all_offers": [
                {
                    "retailer": o.get("retailerName"),
                    "effective_price": o.get("effectiveTotal"),
                    "delivery": o.get("deliveryEstimate"),
                    "in_stock": o.get("availability") == "IN_STOCK"
                }
                for o in offers[:5]
            ]
        }

    @tool
    async def reconcile_activity_requirements(intent: str) -> Dict[str, Any]:
        """
        Analyze a meal or household activity intent (e.g. 'I want to make Maggi tonight', 'make chai', 'cook dal rice').
        Decomposes the activity into required ingredients, inspects live household pantry stock,
        reconciles what is already available in healthy quantities vs what is missing,
        and returns the minimum necessary items to search and purchase.
        
        Args:
            intent: The natural language meal or household activity intent (e.g. 'make Maggi tonight').
        """
        return await reconciliation_service.reconcile_intent(intent)

    @tool
    def record_restraint_decision(
        item_or_category: str,
        reason: str = "Household pantry inventory is healthy; no purchase needed."
    ) -> Dict[str, Any]:
        """
        Record an autonomous restraint decision in the household audit log.
        Use this tool when you decide NOT to buy an item because the household already
        has sufficient inventory or because spending restraint is appropriate.
        
        Args:
            item_or_category: The product or category being evaluated (e.g. 'Fortune Sunflower Oil' or 'Cooking Oils').
            reason: Explanation of why restraint was exercised (e.g. '2.1L in stock, sufficient for ~30 days').
        """
        audit_service.log_decision(item_or_category, "DO_NOTHING", [reason])
        return {
            "verdict": "DO_NOTHING",
            "item": item_or_category,
            "action": "RESTRAINT_RECORDED",
            "reason": reason,
            "message": f"Autonomous restraint logged for {item_or_category}. Zero spend committed."
        }

    @tool
    async def evaluate_and_execute_purchase(
        product_id: str,
        quantity: int = 1,
        reason: str = "Automated household replenishment",
        confidence: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        DETERMINISTIC GUARDED ACTION: Propose purchasing a product.
        
        This tool passes the request through the Python deterministic safety engine:
        - Checks policy rules (blocked vs allowed)
        - Verifies pantry stock needs
        - Verifies remaining monthly budget
        - Verifies single-item auto-buy limit (e.g. ₹500)
        - Verifies autonomy profile
        
        Outcomes:
        - If AUTO: Executes simulated checkout, deducts spend, updates pantry, logs audit trail, returns success.
        - If ASK: Blocks execution, preserves budget, returns exact reasons why user confirmation is needed.
        - If BLOCKED / WAIT / DO_NOTHING: Blocks execution with safety explanation.
        
        Args:
            product_id: The ID of the product to purchase.
            quantity: Quantity to order (default: 1).
            reason: Agent's rationale for ordering.
            confidence: Optional confidence override ('HIGH' or 'LOW'). If omitted, dynamically resolved from pantry tracking.
        """
        # 1. Fetch product
        product = await commerce_adapter.get_product(product_id)
        if not product:
            return {
                "verdict": "ERROR",
                "executed": False,
                "reasons": [f"Product with ID '{product_id}' was not found in catalog."]
            }
        
        unit_price = product.get("price", 0)
        total_price = unit_price * max(1, quantity)
        product_eval = {**product, "price": total_price}
        
        # Determine confidence dynamically if not explicitly specified
        eval_confidence = confidence
        if not eval_confidence:
            pantry_items = inventory_service.get_all() if hasattr(inventory_service, "get_all") else []
            for item in pantry_items:
                if item.get("product_id") == product_id or (product.get("name") and product["name"].lower() in item.get("name", "").lower()):
                    item_conf = item.get("confidence", 0.9)
                    eval_confidence = "LOW" if item_conf < 0.7 else "HIGH"
                    break
            if not eval_confidence:
                eval_confidence = "HIGH"

        # 2. Evaluate with deterministic decision engine
        decision, reasons = await decision_engine.evaluate(product_eval, {"confidence": eval_confidence})
        
        # 3. Log decision to audit trail
        audit_service.log_decision(product["name"], decision, reasons)
        
        if decision == "AUTO":
            # Execute simulated transaction
            try:
                cart_id = await commerce_adapter.create_cart()
                try:
                    await commerce_adapter.add_to_cart(cart_id, product_id, quantity)
                except TypeError:
                    await commerce_adapter.add_to_cart(cart_id, product_id)
                order = await commerce_adapter.checkout(cart_id)
                if not order or order.get("status") == "FAILED" or "error" in order:
                    raise RuntimeError(order.get("error") if order else "Commerce checkout failed")
                await budget_service.record_spend(total_price)
                inventory_service.add_to_pantry(
                    product.get("category", "Grocery"),
                    product["name"],
                    float(quantity),
                    product.get("unit", "pack")
                )
                return {
                    "verdict": "AUTO",
                    "executed": True,
                    "order_id": order.get("id", "sim_order_001"),
                    "mode": "SIMULATED_PURCHASE",
                    "product_name": product["name"],
                    "quantity": quantity,
                    "total_cost": total_price,
                    "reasons": reasons,
                    "message": f"Successfully simulated purchase of {quantity}x {product['name']} for ₹{total_price}. Inventory and budget updated."
                }
            except Exception as e:
                return {
                    "verdict": "ASK",
                    "executed": False,
                    "product_name": product["name"],
                    "total_cost": total_price,
                    "reasons": reasons + [f"Simulated checkout encountered an error: {str(e)}"],
                    "message": f"Checkout could not be completed automatically: {str(e)}"
                }
        
        elif decision == "ASK":
            return {
                "verdict": "ASK",
                "executed": False,
                "product_name": product["name"],
                "quantity": quantity,
                "total_cost": total_price,
                "reasons": reasons,
                "message": f"Purchase requires explicit user confirmation. Reasons: {', '.join(reasons)}"
            }
        elif decision == "BLOCKED":
            return {
                "verdict": "BLOCKED",
                "executed": False,
                "product_name": product["name"],
                "reasons": reasons,
                "message": f"Purchase blocked by safety policy. Reasons: {', '.join(reasons)}"
            }
        elif decision == "WAIT":
            return {
                "verdict": "WAIT",
                "executed": False,
                "product_name": product["name"],
                "reasons": reasons,
                "message": f"Purchase deferred. Recommendation is to wait for price drop or deal. Reasons: {', '.join(reasons)}"
            }
        elif decision == "DO_NOTHING":
            return {
                "verdict": "DO_NOTHING",
                "executed": False,
                "product_name": product["name"],
                "reasons": reasons,
                "message": f"No purchase needed. Household already has sufficient inventory. Reasons: {', '.join(reasons)}"
            }
            
        return {
            "verdict": decision,
            "executed": False,
            "product_name": product["name"],
            "reasons": reasons,
            "message": f"Status: {decision}."
        }

    @tool
    def manage_household_reminder(
        action: str = "list",
        reminder_id: Optional[str] = None,
        title: Optional[str] = None,
        message: Optional[str] = None,
        priority: str = "MEDIUM",
        reminder_type: str = "INVENTORY",
        hours_until_due: int = 24,
        status: Optional[str] = "ACTIVE"
    ) -> Dict[str, Any]:
        """
        Manage household reminders and alerts.
        Actions: 'list', 'create', 'snooze', 'complete', 'dismiss'.
        Allows NOVA to inspect, schedule, or resolve tasks for replenishment, expiration, or budget.
        """
        if not reminder_engine:
            return {"error": "Reminder engine not configured", "status": "FAILED"}

        act = action.lower()
        if act == "list":
            st = status.upper() if status and status.upper() != "ALL" else None
            reminders = reminder_engine.get_reminders(status=st)
            return {"status": "SUCCESS", "count": len(reminders), "reminders": reminders}
        elif act == "create":
            if not title or not message:
                return {"error": "Title and message are required to create a reminder"}
            new_r = reminder_engine.create_reminder(
                type=reminder_type.upper(),
                title=title,
                message=message,
                priority=priority.upper(),
                hours_until_due=hours_until_due
            )
            audit_service.log_decision(title, "REMINDER_CREATED", [message])
            return {"status": "SUCCESS", "action": "created", "reminder": new_r}
        elif act == "snooze" and reminder_id:
            res = reminder_engine.snooze(reminder_id, hours=hours_until_due)
            return {"status": "SUCCESS" if res else "NOT_FOUND", "reminder": res}
        elif act == "complete" and reminder_id:
            res = reminder_engine.complete(reminder_id)
            return {"status": "SUCCESS" if res else "NOT_FOUND", "reminder": res}
        elif act == "dismiss" and reminder_id:
            res = reminder_engine.dismiss(reminder_id)
            return {"status": "SUCCESS" if res else "NOT_FOUND", "reminder": res}
        return {"error": f"Invalid action '{action}' or missing reminder_id", "status": "FAILED"}

    @tool
    def update_household_policy(
        action: str,
        category: Optional[str] = None,
        auto_limit: Optional[float] = None,
        monthly_budget: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update household purchasing policy, category permissions, or spend limits.
        Actions:
          - 'whitelist_auto': set category to automatic purchase without asking.
          - 'require_ask': set category to require explicit user confirmation.
          - 'restrict_category': block/restrict category completely from purchasing.
          - 'set_limits': update auto_limit (₹) or monthly_budget (₹).
        """
        act = action.lower()
        if category and hasattr(policy_service, "set_category_policy"):
            if "auto" in act or "whitelist" in act:
                policy_service.set_category_policy(category, "automatic")
                audit_service.log_decision(category, "POLICY_UPDATED", [f"Moved {category} to automatic auto-buy"])
            elif "ask" in act:
                policy_service.set_category_policy(category, "ask")
                audit_service.log_decision(category, "POLICY_UPDATED", [f"Moved {category} to require confirmation (ASK)"])
            elif "restrict" in act or "block" in act:
                policy_service.set_category_policy(category, "restricted")
                audit_service.log_decision(category, "POLICY_UPDATED", [f"Restricted category {category}"])

        if auto_limit is not None and hasattr(budget_service, "set_auto_limit"):
            budget_service.set_auto_limit(float(auto_limit))
            audit_service.log_decision("Auto-Buy Limit", "BUDGET_UPDATED", [f"Set auto-buy limit to ₹{auto_limit}"])
        if monthly_budget is not None and hasattr(budget_service, "set_budget"):
            budget_service.set_budget(float(monthly_budget))
            audit_service.log_decision("Monthly Budget", "BUDGET_UPDATED", [f"Set monthly budget to ₹{monthly_budget}"])

        return {
            "status": "SUCCESS",
            "policy": policy_service.get_rules() if hasattr(policy_service, "get_rules") else {},
            "budget": budget_service.get_status() if hasattr(budget_service, "get_status") else {}
        }

    @tool
    def update_pantry_stock(
        item_name: str,
        quantity: float,
        unit: str = "units",
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add or update quantity of an item in the household pantry inventory.
        Use when user reports consuming, buying, or replenishing pantry items.
        """
        if hasattr(inventory_service, "update_item"):
            res = inventory_service.update_item(item_name, quantity=quantity, unit=unit, status=status)
            audit_service.log_decision(item_name, "PANTRY_UPDATED", [f"Quantity set to {quantity} {unit}"])
            return {"status": "SUCCESS", "item": res}
        return {"error": "Inventory update not supported", "status": "FAILED"}

    @tool
    def report_item_depleted(item_name: str) -> Dict[str, Any]:
        """
        Report that a household pantry item is completely empty or out of stock.
        Sets stock quantity to 0 and marks status as LOW for automated replenishment.
        """
        if hasattr(inventory_service, "report_depleted"):
            res = inventory_service.report_depleted(item_name)
            audit_service.log_decision(item_name, "ITEM_DEPLETED", [f"Marked {item_name} as depleted (0 stock)"])
            return {"status": "SUCCESS", "depleted_item": res, "item": res, "message": f"{item_name} marked as empty."}
        return {"error": "Inventory update not supported", "status": "FAILED"}

    @tool
    def get_price_watch_items(filter_verdict: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspect price-tracked household items to check whether NOVA recommends buying now
        or waiting for price drops / deal timing.
        """
        if not savings_engine:
            return {"error": "Savings engine not configured", "opportunities": []}
        savings = savings_engine.get_savings_opportunities()
        opps = savings.get("opportunities", [])
        if filter_verdict:
            opps = [o for o in opps if o.get("action", "").upper() == filter_verdict.upper()]
        return {
            "total_tracked": len(opps),
            "opportunities": opps,
            "total_potential_saving": savings.get("total_potential_saving", 0),
            "summary": savings.get("summary", "")
        }

    return [
        get_pantry_inventory,
        get_purchase_history,
        get_household_overview,
        get_budget_status,
        check_category_policy,
        search_catalog,
        compare_product_offers,
        reconcile_activity_requirements,
        record_restraint_decision,
        evaluate_and_execute_purchase,
        manage_household_reminder,
        update_household_policy,
        update_pantry_stock,
        report_item_depleted,
        get_price_watch_items
    ]

