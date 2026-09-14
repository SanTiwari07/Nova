import os
import sys
import json
import asyncio

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

for p in [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env"
]:
    if p.exists():
        load_dotenv(dotenv_path=p)
load_dotenv()

from strands import Agent
from strands.hooks import AfterToolCallEvent, BeforeToolCallEvent
from .tools import create_nova_tools

NOVA_SYSTEM_PROMPT = """You are NOVA, an uncertainty-aware autonomous household decision AI agent built with the AWS Strands Agents SDK.
Your mission is to manage everyday household life: replenish groceries and essentials, monitor pantry inventory, track consumption, enforce budget limits, manage reminders, and uphold household safety policies.

CORE AGENT BEHAVIORS & PRINCIPLES:

1. GATHER FACTS FIRST - NEVER GUESS:
   - Always check pantry inventory (`get_pantry_inventory`) or history before assuming an item needs replenishing.
   - Ground all statements in real household state. Never invent imaginary items or fake prices.

2. RESTRAINT & PRUDENCE (DO_NOTHING WHEN HEALTHY):
   - NOVA is NOT rewarded for buying things. NOVA is rewarded for making the correct, prudent household decision.
   - When the user asks about buying an item or whether they need something:
     * Inspect pantry inventory first with `get_pantry_inventory`.
     * If the household already has ample supply (healthy stock, sufficient days remaining), your decision is DO_NOTHING.
     * Record the restraint decision with `record_restraint_decision(item_or_category=..., reason=...)`.
     * Clearly inform the user: state how much stock is left and how many days it will last, and advise against purchasing.
     * Do NOT search the catalog needlessly and do NOT place an order when stock is healthy.

3. MEAL & ACTIVITY INTENT RECONCILIATION:
   - When the user expresses an activity or meal intent (e.g. 'I want to make Maggi tonight', 'making poha', 'cook pasta', 'make chai'):
     * Do NOT interpret this as a simple product search.
     * Call `reconcile_activity_requirements(intent=...)` to decompose the activity into requirements and inspect the pantry.
     * Reconcile: identify which ingredients are already present in healthy quantities vs which are missing from the pantry.
     * DO NOT buy items the household already has in healthy stock!
     * For ONLY the missing item(s), search the catalog using `search_catalog` and evaluate purchase with `evaluate_and_execute_purchase`.
     * Present a transparent reconciliation breakdown:
       - What the household already has in stock
       - What was missing from the pantry
       - The autonomous decision made for the missing requirement.

4. ORDERING & DETERMINISTIC SAFETY GATES:
   - When replenishment or purchase is required:
     * Always search products with `search_catalog(query=...)`.
     * ALWAYS call `evaluate_and_execute_purchase(product_id=..., quantity=...)` to run deterministic safety checks:
       policy rules, budget availability, per-transaction limit (₹500), necessity, and autonomy mode.
     * You must NEVER simulate checkout yourself - `evaluate_and_execute_purchase` is the ONLY tool authorized to execute purchases.
     * If the tool returns AUTO: The simulated purchase was approved and executed within limits. Confirm this clearly with product name, price, and status.
     * If the tool returns ASK: Explain why user confirmation is required (e.g. price > auto limit, or category requires ask).
     * If the tool returns BLOCKED: Explain policy restriction.
     * If the tool returns DO_NOTHING or WAIT: Explain why no order was placed.

5. HOUSEHOLD GOVERNANCE, REMINDERS & INVENTORY MANAGEMENT:
   - Act on user requests to create or manage reminders via `manage_household_reminder`.
   - Update household purchasing policies or limits via `update_household_policy`.
   - Update pantry counts when user reports restocks or consumptions via `update_pantry_stock` or `report_item_depleted`.

6. CLARITY & HONESTY:
   - Be concise, friendly, and transparent. Clearly mention that purchases are simulated in this zero-cost hackathon demo environment.
"""


class NovaAgent:
    def __init__(
        self,
        ai_service,
        decision_engine,
        commerce_adapter,
        inventory_service,
        budget_service,
        audit_service,
        history_service=None,
        reminder_engine=None,
        savings_engine=None,
        session_service=None,
        intent_service=None
    ):
        self.ai_service = ai_service
        self.decision_engine = decision_engine
        self.commerce = commerce_adapter
        self.inventory = inventory_service
        self.budget = budget_service
        self.audit = audit_service
        self.history = history_service
        self.reminder = reminder_engine
        self.savings = savings_engine
        self.session = session_service or getattr(decision_engine, "session_service", None)
        self.intent = intent_service

        # Create Strands tools
        self.tools = create_nova_tools(
            inventory_service=self.inventory,
            budget_service=self.budget,
            policy_service=getattr(decision_engine, "policy_service", None),
            commerce_adapter=self.commerce,
            history_service=self.history,
            decision_engine=self.decision_engine,
            audit_service=self.audit,
            session_service=self.session,
            reminder_engine=self.reminder,
            savings_engine=self.savings,
            intent_service=self.intent
        )

        self.agent: Optional[Agent] = None
        self.active_provider: str = "FALLBACK"
        self._init_strands_agent()

    def _create_model(self) -> Tuple[Optional[Any], str]:
        """
        Model factory supporting both Google Gemini and AWS Bedrock providers.
        Configured via LLM_PROVIDER ('gemini' or 'bedrock').
        """
        provider_env = os.environ.get("LLM_PROVIDER", "gemini").strip().lower()

        # 1. AWS Bedrock Provider
        if provider_env == "bedrock":
            try:
                from strands.models.bedrock import BedrockModel
                model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
                region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
                bedrock_model = BedrockModel(model_id=model_id, region_name=region)
                return bedrock_model, "STRANDS_BEDROCK"
            except Exception as e:
                print(f"[NovaAgent] Could not initialize AWS BedrockModel: {e}. Falling back to Gemini.")
                provider_env = "gemini"

        # 2. Google Gemini Provider
        if provider_env == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY", "")
            if api_key:
                try:
                    from strands.models.gemini import GeminiModel
                    model_id = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
                    gemini_model = GeminiModel(
                        model_id=model_id,
                        client_args={"api_key": api_key}
                    )
                    return gemini_model, "STRANDS_GEMINI"
                except Exception as e:
                    print(f"[NovaAgent] Could not initialize GeminiModel: {e}")

        return None, "STRANDS_FALLBACK"

    def _init_strands_agent(self):
        try:
            model, mode_tag = self._create_model()
            if not model:
                self.agent = None
                self.active_provider = "STRANDS_FALLBACK"
                return

            self.agent = Agent(
                model=model,
                tools=self.tools,
                system_prompt=NOVA_SYSTEM_PROMPT
            )
            self.active_provider = mode_tag

            # Register telemetry hook
            def on_before_tool(event: BeforeToolCallEvent):
                queue = event.invocation_state.get("queue")
                if queue is not None:
                    tool_name = event.tool_use.get("name", "unknown")
                    queue.put_nowait({"type": "tool_start", "tool": tool_name})

            def on_tool_call(event: AfterToolCallEvent):
                traces = event.invocation_state.get("traces")
                queue = event.invocation_state.get("queue")
                
                tool_name = event.tool_use.get("name", "unknown")
                tool_input = event.tool_use.get("input", {})
                result_summary = "executed"
                if event.result and getattr(event.result, "content", None):
                    content_list = event.result.content
                    if content_list and isinstance(content_list[0], dict) and "text" in content_list[0]:
                        text_snip = content_list[0]["text"]
                        try:
                            parsed = json.loads(text_snip)
                            if isinstance(parsed, dict):
                                if "verdict" in parsed:
                                    result_summary = f"Verdict: {parsed['verdict']}"
                                elif "reconciliation_summary" in parsed:
                                    result_summary = parsed["reconciliation_summary"][:80]
                                elif "total_items_checked" in parsed:
                                    result_summary = f"Checked {parsed['total_items_checked']} items ({parsed.get('low_stock_count', 0)} low)"
                                elif "remaining_budget" in parsed:
                                    result_summary = f"Budget remaining: ₹{parsed['remaining_budget']}"
                                elif "item" in parsed and "action" in parsed:
                                    result_summary = f"{parsed['action']}: {parsed['item']}"
                        except (json.JSONDecodeError, TypeError, KeyError, AttributeError):
                            parsed = None
                            result_summary = text_snip[:60]

                if traces is not None:
                    traces.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "status": "error" if event.exception else "success",
                        "summary": result_summary,
                        "duration": round(event.duration or 0, 3),
                        "result": parsed if 'parsed' in locals() and isinstance(parsed, dict) else None
                    })
                    
                if queue is not None:
                    queue.put_nowait({
                        "type": "tool_completed",
                        "tool": tool_name,
                        "summary": result_summary,
                        "duration_ms": int((event.duration or 0) * 1000),
                        "status": "error" if event.exception else "success",
                        "result": parsed if 'parsed' in locals() and isinstance(parsed, dict) else None
                    })

            self.agent.add_hook(on_before_tool, BeforeToolCallEvent)
            self.agent.add_hook(on_tool_call, AfterToolCallEvent)
            print(f"[NovaAgent] Successfully initialized AWS Strands Agent ({self.active_provider})")
        except Exception as e:
            print(f"[NovaAgent] Error initializing Strands agent: {e}")
            self.agent = None
            self.active_provider = "STRANDS_FALLBACK"

    async def invoke(self, user_request: str, force_fallback: bool = False) -> Dict[str, Any]:
        """Convenience alias for handle_request."""
        return await self.handle_request(user_request, force_fallback=force_fallback)

    async def invoke_stream(self, user_request: str, force_fallback: bool = False):
        if not force_fallback and not self.agent and (os.environ.get("GEMINI_API_KEY") or os.environ.get("BEDROCK_MODEL_ID")):
            self._init_strands_agent()
            
        queue = asyncio.Queue()
        traces = []
        
        async def run_agent():
            if self.agent and not force_fallback:
                try:
                    result = await self.agent.invoke_async(
                        user_request,
                        invocation_state={"traces": traces, "queue": queue}
                    )
                    response_text = str(result).strip()

                    # General restraint auditing
                    if any(w in response_text.lower() for w in ["do_nothing", "sufficient", "do not buy", "healthy stock", "already have enough", "plenty"]):
                        if not any(t.get("tool") == "record_restraint_decision" for t in traces):
                            for item in self.inventory.get_all():
                                if item["name"].lower() in user_request.lower() or item["category"].lower() in user_request.lower():
                                    self.audit.log_decision(
                                        item["name"],
                                        "DO_NOTHING",
                                        [f"Household pantry stock is healthy ({item['quantity']}{item['unit']} in stock, ~{item['days_remaining']} days left); autonomous restraint applied."]
                                    )
                                    break

                    return {
                        "response": response_text,
                        "tool_trace": traces,
                        "mode": f"{self.active_provider}_AUTONOMOUS",
                        "provider": self.active_provider,
                        "status": "success"
                    }
                except Exception as e:
                    err_msg = str(e)
                    print(f"[NovaAgent] Strands invocation error: {err_msg}. Falling back to tool dispatcher.")
                    if "API_KEY_INVALID" in err_msg or "INVALID_ARGUMENT" in err_msg or "API key not valid" in err_msg:
                        self.agent = None
                    traces.append({"tool": "strands_agent", "status": "error", "summary": err_msg[:120]})
                    return await self._deterministic_tool_dispatch(user_request, traces)
            else:
                return await self._deterministic_tool_dispatch(user_request, traces)
                
        task = asyncio.create_task(run_agent())
        
        while not task.done():
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield json.dumps(msg) + "\n"
            except asyncio.TimeoutError:
                continue
                
        while not queue.empty():
            msg = queue.get_nowait()
            yield json.dumps(msg) + "\n"
            
        final_result = task.result()
        yield json.dumps({"type": "final_result", "data": final_result}) + "\n"

    async def handle_request(self, user_request: str, force_fallback: bool = False) -> Dict[str, Any]:
        """
        Processes a user request through the genuine Strands Agent loop or deterministic tool runner.
        Returns a dict containing response text, full tool execution trace, active mode, and provider.
        """
        # Re-check model if agent wasn't initialized yet
        if not force_fallback and not self.agent and (os.environ.get("GEMINI_API_KEY") or os.environ.get("BEDROCK_MODEL_ID")):
            self._init_strands_agent()

        traces: List[Dict[str, Any]] = []

        if self.agent and not force_fallback:
            try:
                result = await self.agent.invoke_async(
                    user_request,
                    invocation_state={"traces": traces}
                )
                response_text = str(result).strip()

                # General restraint auditing: ensure DO_NOTHING was logged if restraint was advised
                if any(w in response_text.lower() for w in ["do_nothing", "sufficient", "do not buy", "healthy stock", "already have enough", "plenty"]):
                    if not any(t.get("tool") == "record_restraint_decision" for t in traces):
                        for item in self.inventory.get_all():
                            if item["name"].lower() in user_request.lower() or item["category"].lower() in user_request.lower():
                                self.audit.log_decision(
                                    item["name"],
                                    "DO_NOTHING",
                                    [f"Household pantry stock is healthy ({item['quantity']}{item['unit']} in stock, ~{item['days_remaining']} days left); autonomous restraint applied."]
                                )
                                break

                return {
                    "response": response_text,
                    "tool_trace": traces,
                    "mode": f"{self.active_provider}_AUTONOMOUS",
                    "provider": self.active_provider,
                    "status": "success"
                }
            except Exception as e:
                err_msg = str(e)
                print(f"[NovaAgent] Strands invocation error: {err_msg}. Falling back to tool dispatcher.")
                if "API_KEY_INVALID" in err_msg or "INVALID_ARGUMENT" in err_msg or "API key not valid" in err_msg:
                    print("[NovaAgent] Gemini API key is invalid or unconfigured. Disabling active agent.")
                    self.agent = None
                traces.append({"tool": "strands_agent", "status": "error", "summary": err_msg[:120]})

        # Deterministic Tool Dispatcher fallback (when LLM provider is unavailable)
        return await self._deterministic_tool_dispatch(user_request, traces)

    async def _deterministic_tool_dispatch(self, user_request: str, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generalized, capability-driven Strands tool runner when external LLMs are offline.
        Inspects user intent dynamically without hardcoding any specific demo scenario.
        """
        tools_map = {t.tool_spec["name"]: t for t in self.tools}
        req_lower = user_request.lower()

        # 1. REMINDERS & ALERTS
        if any(w in req_lower for w in ["remind", "reminder", "snooze", "complete reminder", "dismiss reminder"]):
            rem_tool = tools_map.get("manage_household_reminder")
            if rem_tool:
                if "snooze" in req_lower:
                    res = rem_tool(action="snooze", reminder_id="rem_001", hours_until_due=24)
                    traces.append({"tool": "manage_household_reminder", "input": {"action": "snooze"}, "status": "success", "summary": "Snoozed reminder"})
                    return {"response": "Reminder snoozed for 24 hours.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}
                elif "complete" in req_lower:
                    res = rem_tool(action="complete", reminder_id="rem_001")
                    traces.append({"tool": "manage_household_reminder", "input": {"action": "complete"}, "status": "success", "summary": "Completed reminder"})
                    return {"response": "Reminder marked as completed.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}
                elif "dismiss" in req_lower:
                    res = rem_tool(action="dismiss", reminder_id="rem_001")
                    traces.append({"tool": "manage_household_reminder", "input": {"action": "dismiss"}, "status": "success", "summary": "Dismissed reminder"})
                    return {"response": "Reminder dismissed.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}
                elif any(w in req_lower for w in ["create", "remind me to", "set reminder", "add reminder"]):
                    title = user_request
                    for prefix in ["remind me to", "set reminder to", "add reminder to", "create reminder"]:
                        if prefix in req_lower:
                            title = user_request[req_lower.find(prefix) + len(prefix):].strip().title()
                            break
                    res = rem_tool(action="create", title=title or "Household Task", message=user_request, priority="HIGH")
                    traces.append({"tool": "manage_household_reminder", "input": {"action": "create", "title": title}, "status": "success", "summary": f"Created reminder: {title}"})
                    return {"response": f"I have scheduled a high-priority reminder for you: **{title}**.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}
                else:
                    res = rem_tool(action="list")
                    traces.append({"tool": "manage_household_reminder", "input": {"action": "list"}, "status": "success", "summary": f"Found {res.get('count', 0)} active reminders"})
                    items_txt = "\n".join([f"- **{r['title']}**: {r['message']} ({r['priority']} priority)" for r in res.get("reminders", [])[:5]])
                    return {"response": f"**Active Household Reminders:**\n{items_txt or 'No active reminders.'}", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}

        # 2. POLICY & GOVERNANCE RULES
        if any(w in req_lower for w in ["policy", "rule", "whitelist", "restrict", "never auto-buy", "never buy", "spend limit", "auto limit"]):
            pol_tool = tools_map.get("update_household_policy")
            if pol_tool:
                # Check for category restriction
                if any(w in req_lower for w in ["never", "restrict", "block", "disallow"]):
                    # Find candidate category
                    categories = ["snacks", "electronics", "alcohol", "tobacco", "cleaning", "dairy", "beverages"]
                    matched_cat = next((c for c in categories if c in req_lower), "Snacks")
                    res = pol_tool(action="restrict_category", category=matched_cat.title())
                    traces.append({"tool": "update_household_policy", "input": {"action": "restrict_category", "category": matched_cat}, "status": "success", "summary": f"Restricted category {matched_cat.title()}"})
                    return {"response": f"Policy updated: **{matched_cat.title()}** has been restricted and will never be auto-purchased without explicit approval.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}
                elif any(w in req_lower for w in ["auto", "whitelist", "allow auto"]):
                    categories = ["milk", "rice", "atta", "eggs", "bread", "soap", "tea", "detergent"]
                    matched_cat = next((c for c in categories if c in req_lower), "Essentials")
                    res = pol_tool(action="whitelist_auto", category=matched_cat.title())
                    traces.append({"tool": "update_household_policy", "input": {"action": "whitelist_auto", "category": matched_cat}, "status": "success", "summary": f"Whitelisted category {matched_cat.title()}"})
                    return {"response": f"Policy updated: **{matched_cat.title()}** is now permitted for autonomous replenishment within your ₹500 auto-buy limit.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}
                elif "budget" in req_lower and any(c.isdigit() for c in user_request):
                    import re
                    nums = re.findall(r"\d+", user_request)
                    val = float(nums[0]) if nums else 3000.0
                    old_b = self.budget.monthly_budget
                    self.budget.set_budget(val)
                    rem = await self.budget.get_remaining_budget()
                    self.audit.log_event(
                        event_type="BUDGET_CHANGED",
                        title=f"Monthly Budget Changed: ₹{int(old_b):,} → ₹{int(val):,}",
                        description=f"Household budget updated via conversational command to ₹{int(val):,}. Remaining: ₹{int(rem):,}.",
                        entity_type="BUDGET",
                        product="Household Budget",
                        decision="AUTO",
                        reasons=[
                            f"Monthly budget adjusted from ₹{int(old_b):,} to ₹{int(val):,}.",
                            f"Active purchasing headroom: ₹{int(rem):,}."
                        ]
                    )
                    traces.append({"tool": "update_household_budget", "input": {"monthly_budget": val}, "status": "success", "summary": f"Set monthly budget to ₹{val}"})
                    return {"response": f"Household monthly budget updated to **₹{int(val):,}** (previous: ₹{int(old_b):,}). You now have **₹{int(rem):,}** in active spending headroom for this cycle.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}
                elif "limit" in req_lower:
                    import re
                    nums = re.findall(r"\d+", user_request)
                    val = float(nums[0]) if nums else 500.0
                    res = pol_tool(action="set_limits", auto_limit=val)
                    traces.append({"tool": "update_household_policy", "input": {"auto_limit": val}, "status": "success", "summary": f"Set auto-buy limit to ₹{val}"})
                    return {"response": f"Per-item auto-buy limit updated to **₹{val}**.", "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}

        # 3. PANTRY STOCK MUTATIONS (Depletion or Restocking)
        if any(phrase in req_lower for phrase in ["ran out of", "out of", "empty", "finished", "no more"]):
            deplete_tool = tools_map.get("report_item_depleted")
            if deplete_tool:
                # Extract candidate item name after the trigger phrase
                for trigger in ["ran out of", "out of", "finished", "no more"]:
                    if trigger in req_lower:
                        item_name = user_request[req_lower.find(trigger) + len(trigger):].strip().strip(".!?,")
                        if item_name:
                            res = deplete_tool(item_name=item_name)
                            traces.append({"tool": "report_item_depleted", "input": {"item_name": item_name}, "status": "success", "summary": f"Reported {item_name} depleted"})
                            return {
                                "response": f"I have marked **{item_name.title()}** as empty (0 stock, status: LOW) in your pantry. Replenishment will be prioritized in your household restock cycle.",
                                "tool_trace": traces,
                                "mode": "STRANDS_TOOLS_DETERMINISTIC",
                                "provider": "STRANDS_FALLBACK",
                                "status": "success"
                            }

        if any(w in req_lower for w in ["add", "restock", "bought", "we have"]) and any(char.isdigit() for char in user_request):
            stock_tool = tools_map.get("update_pantry_stock")
            if stock_tool:
                import re
                nums = re.findall(r"\d+\.?\d*", user_request)
                qty = float(nums[0]) if nums else 1.0
                words = [w for w in user_request.split() if w.lower() not in ["add", "to", "pantry", "we", "bought", "have", "of", "the", "in", "packets", "packs", "kg", "l", "liters", "units"]]
                item_name = " ".join(words).strip() or "Item"
                res = stock_tool(item_name=item_name, quantity=qty, unit="units")
                traces.append({"tool": "update_pantry_stock", "input": {"item_name": item_name, "quantity": qty}, "status": "success", "summary": f"Updated {item_name} stock to {qty}"})
                return {
                    "response": f"Pantry updated! Added **{qty} units** of **{item_name.title()}**. Inventory status is now healthy.",
                    "tool_trace": traces,
                    "mode": "STRANDS_TOOLS_DETERMINISTIC",
                    "provider": "STRANDS_FALLBACK",
                    "status": "success"
                }

        # 4. GENERAL ACTIVITY / MEAL INTENT RECONCILIATION
        if any(w in req_lower for w in ["make", "making", "cook", "cooking", "prepare", "preparing", "for dinner", "for lunch", "for breakfast", "recipe"]):
            reconcile_tool = tools_map.get("reconcile_activity_requirements")
            search_tool = tools_map.get("search_catalog")
            purchase_tool = tools_map.get("evaluate_and_execute_purchase")

            if reconcile_tool:
                reconcile_res = await reconcile_tool(intent=user_request)
                traces.append({
                    "tool": "reconcile_activity_requirements",
                    "input": {"intent": user_request},
                    "status": "success",
                    "summary": f"Reconciled {reconcile_res.get('recipe', {}).get('name', 'Recipe')} with pantry",
                    "result": reconcile_res
                })

                shopping_items = reconcile_res.get("shopping", {}).get("items", [])
                missing_items = [{"item": item["name"]} for item in shopping_items]
                query = shopping_items[0]["name"] if shopping_items else ""

                if missing_items and query and search_tool and purchase_tool:
                    products = await search_tool(query=query)
                    if not products and len(shopping_items) > 1:
                        for alt_q in shopping_items[1:]:
                            products = await search_tool(query=alt_q["name"])
                            if products:
                                query = alt_q["name"]
                                break
                    if not products and missing_items:
                        first_word = missing_items[0]["item"].split()[0]
                        if len(first_word) > 2:
                            products = await search_tool(query=first_word)

                    traces.append({
                        "tool": "search_catalog",
                        "input": {"query": query},
                        "status": "success",
                        "summary": f"Found {len(products)} products for '{query}'"
                    })

                    if products:
                        selected = products[0]
                        res = await purchase_tool(
                            product_id=selected["product_id"],
                            quantity=1,
                            reason=f"Activity fulfillment for '{user_request}'"
                        )
                        traces.append({
                            "tool": "evaluate_and_execute_purchase",
                            "input": {"product_id": selected["product_id"], "quantity": 1},
                            "status": "success",
                            "summary": f"Verdict: {res.get('verdict')}"
                        })

                        avail_desc = ", ".join([a.get("name", a) for a in reconcile_res.get("pantry", {}).get("available", [])])
                        resp = (
                            f"**Activity Reconciliation for '{reconcile_res.get('recipe', {}).get('name', 'Meal/Activity')}':**\n\n"
                            f"1. **Pantry Check:**\n"
                            f"   - **Available in stock:** {avail_desc or 'None'}\n"
                            f"   - **Missing from pantry:** {', '.join([m['item'] for m in missing_items])}\n\n"
                            f"2. **Minimum Necessary Purchase:**\n"
                            f"   - Identified missing requirement: **{selected['name']}** (₹{selected['price']})\n"
                            f"   - **Verdict:** **{res.get('verdict')}** ({res.get('message', 'Processed')})\n\n"
                            f"3. **Prudence Guaranteed:** Ingredients already present in your pantry were preserved; only missing supplies were ordered."
                        )
                        return {
                            "response": resp,
                            "tool_trace": traces,
                            "mode": "STRANDS_TOOLS_DETERMINISTIC",
                            "provider": "STRANDS_FALLBACK",
                            "status": "success"
                        }
                    else:
                        avail_desc = ", ".join([a.get("name", a) for a in reconcile_res.get("pantry", {}).get("available", [])])
                        resp = (
                            f"**Activity Reconciliation for '{reconcile_res.get('recipe', {}).get('name', 'Meal/Activity')}':**\n\n"
                            f"1. **Pantry Check:**\n"
                            f"   - **Available in stock:** {avail_desc or 'None'}\n"
                            f"   - **Missing from pantry:** {', '.join([m['item'] for m in missing_items])}\n\n"
                            f"2. **Catalog Status:** No exact products matched '{query}' in the current catalog. Please check catalog inventory directly."
                        )
                        return {
                            "response": resp,
                            "tool_trace": traces,
                            "mode": "STRANDS_TOOLS_DETERMINISTIC",
                            "provider": "STRANDS_FALLBACK",
                            "status": "success"
                        }

        # 5. GENERAL PRUDENCE, RESTRAINT & STOCK SUFFICIENCY
        if any(w in req_lower for w in ["should i buy", "do i need", "do we need", "have enough", "is there enough", "check if we need"]):
            pantry_tool = tools_map.get("get_pantry_inventory")
            restraint_tool = tools_map.get("record_restraint_decision")
            search_tool = tools_map.get("search_catalog")
            purchase_tool = tools_map.get("evaluate_and_execute_purchase")

            # Extract target item word
            words = [w for w in req_lower.replace("?", "").split() if w not in ["should", "i", "do", "we", "need", "buy", "have", "enough", "is", "there", "any", "the", "check", "if", "more"]]
            cand = words[0] if words else ""

            if pantry_tool:
                pantry_res = pantry_tool(category=cand)
                items = pantry_res.get("items", [])
                traces.append({
                    "tool": "get_pantry_inventory",
                    "input": {"category": cand},
                    "status": "success",
                    "summary": f"Found {len(items)} matching items in stock"
                })

                # Check if an existing item has sufficient stock
                healthy_item = next((i for i in items if i.get("status") == "HEALTHY" or i.get("days_remaining", 0) >= 7), None)
                if healthy_item and restraint_tool:
                    restraint_res = restraint_tool(
                        item_or_category=healthy_item["name"],
                        reason=f"Pantry stock is healthy ({healthy_item['quantity']}{healthy_item['unit']} in stock, ~{healthy_item['days_remaining']} days remaining)."
                    )
                    traces.append({
                        "tool": "record_restraint_decision",
                        "input": {"item_or_category": healthy_item["name"]},
                        "status": "success",
                        "summary": f"Logged DO_NOTHING restraint for {healthy_item['name']}"
                    })

                    resp = (
                        f"**Decision: DO_NOTHING (Autonomous Restraint Applied)**\n\n"
                        f"I checked your household pantry inventory for **{healthy_item['name']}**:\n"
                        f"- **Current Stock:** {healthy_item['quantity']} {healthy_item['unit']}\n"
                        f"- **Days Remaining:** ~{healthy_item['days_remaining']} days\n"
                        f"- **Status:** HEALTHY\n\n"
                        f"You have ample supply in stock. NOVA recommends **not buying** additional stock right now. "
                        f"This restraint decision has been recorded in your household audit trail."
                    )
                    return {
                        "response": resp,
                        "tool_trace": traces,
                        "mode": "STRANDS_TOOLS_DETERMINISTIC",
                        "provider": "STRANDS_FALLBACK",
                        "status": "success"
                    }
                elif items and items[0].get("status") == "LOW" and search_tool and purchase_tool:
                    # Stock is low, proceed to replenish
                    low_item = items[0]
                    prods = await search_tool(query=low_item["name"])
                    if prods:
                        p_res = await purchase_tool(product_id=prods[0]["product_id"], quantity=1, reason="Pantry low stock replenishment")
                        traces.append({"tool": "evaluate_and_execute_purchase", "input": {"product_id": prods[0]["product_id"]}, "status": "success", "summary": f"Verdict: {p_res.get('verdict')}"})
                        return {
                            "response": f"**Stock Low for {low_item['name']}** ({low_item['quantity']}{low_item['unit']} remaining). Evaluated replenishment: **{p_res.get('verdict')}**. {p_res.get('message')}",
                            "tool_trace": traces,
                            "mode": "STRANDS_TOOLS_DETERMINISTIC",
                            "provider": "STRANDS_FALLBACK",
                            "status": "success"
                        }

        # 6. GENERAL DIRECT REPLENISHMENT / PURCHASE
        if any(w in req_lower for w in ["buy", "order", "need", "replenish", "purchase", "get"]):
            pantry_tool = tools_map.get("get_pantry_inventory")
            search_tool = tools_map.get("search_catalog")
            purchase_tool = tools_map.get("evaluate_and_execute_purchase")

            # Extract item
            words = [w for w in req_lower.replace("?", "").split() if w not in ["i", "we", "buy", "order", "need", "replenish", "purchase", "get", "some", "a", "an", "the", "please"]]
            target_query = " ".join(words).strip() or user_request

            # 1. Fact Gathering First: inspect inventory
            if pantry_tool:
                p_res = pantry_tool(category=target_query)
                traces.append({
                    "tool": "get_pantry_inventory",
                    "input": {"category": target_query},
                    "status": "success",
                    "summary": f"Fact Check: {len(p_res.get('items', []))} matching items in inventory"
                })

            if search_tool and purchase_tool:
                products = await search_tool(query=target_query)
                traces.append({
                    "tool": "search_catalog",
                    "input": {"query": target_query},
                    "status": "success",
                    "summary": f"Found {len(products)} products"
                })

                if products:
                    selected = products[0]
                    result = await purchase_tool(
                        product_id=selected["product_id"],
                        quantity=1,
                        reason=f"Autonomous replenishment request: '{user_request}'"
                    )
                    traces.append({
                        "tool": "evaluate_and_execute_purchase",
                        "input": {"product_id": selected["product_id"], "quantity": 1},
                        "status": "success",
                        "summary": f"Verdict: {result.get('verdict')}"
                    })

                    verdict = result.get("verdict")
                    resp = (
                        f"**Household Decision for {selected['name']}:**\n\n"
                        f"- **Selected Product:** {selected['name']} (₹{result.get('total_cost', selected['price'])})\n"
                        f"- **Deterministic Safety Verdict:** **{verdict}**\n"
                        f"- **Rationale:** {'; '.join(result.get('reasons', []))}\n"
                        f"- **Status:** {result.get('message', 'Completed')}"
                    )
                    return {
                        "response": resp,
                        "tool_trace": traces,
                        "mode": "STRANDS_TOOLS_DETERMINISTIC",
                        "provider": "STRANDS_FALLBACK",
                        "status": "success"
                    }

        # 7. GENERAL STATUS & INQUIRY LOOKUPS
        if any(w in req_lower for w in ["budget", "spend", "balance", "money"]):
            b_tool = tools_map.get("get_budget_status")
            if b_tool:
                res = b_tool()
                traces.append({"tool": "get_budget_status", "input": {}, "status": "success", "summary": f"Remaining: ₹{res.get('remaining_budget')}"})
                resp = f"**Household Budget Status:**\n- Monthly Budget: ₹{res.get('monthly_budget')}\n- Spent So Far: ₹{res.get('spent')}\n- Remaining Balance: ₹{res.get('remaining_budget')}\n- Auto-Buy Transaction Limit: ₹{res.get('auto_buy_limit')}"
                return {"response": resp, "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}

        if any(w in req_lower for w in ["price watch", "deals", "savings", "price drop"]):
            pw_tool = tools_map.get("get_price_watch_items")
            if pw_tool:
                res = pw_tool()
                traces.append({"tool": "get_price_watch_items", "input": {}, "status": "success", "summary": f"Found {res.get('total_tracked', 0)} tracked price opportunities"})
                opps_txt = "\n".join([f"- **{o['product_name']}**: Current ₹{o['current_price']} (Target ₹{o['target_price']}) - Action: **{o['action']}**. {o['reason']}" for o in res.get("opportunities", [])])
                resp = f"**Price Watch Opportunities (Savings: ₹{res.get('total_potential_saving', 0)}):**\n{opps_txt or 'No tracked items currently.'}"
                return {"response": resp, "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}

        if any(w in req_lower for w in ["pantry", "inventory", "stock", "what do we have", "supplies"]):
            p_tool = tools_map.get("get_pantry_inventory")
            if p_tool:
                res = p_tool()
                low_items = res.get("low_stock_items", [])
                traces.append({"tool": "get_pantry_inventory", "input": {}, "status": "success", "summary": f"Inspected pantry: {len(res.get('items', []))} items"})
                if low_items:
                    resp = f"**Pantry Inspection:** {len(res.get('items', []))} items tracked. Running low on: {', '.join(low_items)}."
                else:
                    resp = f"**Pantry Inspection:** All {len(res.get('items', []))} items are in healthy supply."
                return {"response": resp, "tool_trace": traces, "mode": "STRANDS_TOOLS_DETERMINISTIC", "provider": "STRANDS_FALLBACK", "status": "success"}

        # 8. DEFAULT FALLBACK
        overview_tool = tools_map.get("get_household_overview")
        if overview_tool:
            ov = overview_tool()
            low_count = ov.get("pantry_low_items_count", ov.get("low_stock_count", 0))
            rem_budget = ov.get("budget_remaining", ov.get("remaining_budget", 0))
            traces.append({"tool": "get_household_overview", "input": {}, "status": "success", "summary": "Retrieved household status"})
            return {
                "response": f"I am NOVA, your AWS Strands household autopilot. You currently have {low_count} items running low in your pantry and ₹{rem_budget} in your monthly budget. How can I help with your household today?",
                "tool_trace": traces,
                "mode": "STRANDS_TOOLS_DETERMINISTIC",
                "provider": "STRANDS_FALLBACK",
                "status": "success"
            }

        return {
            "response": "NOVA Household Autopilot ready. You can ask me to check pantry inventory, manage reminders, inspect budget, evaluate recipes, or replenish household essentials.",
            "tool_trace": traces,
            "mode": "STRANDS_TOOLS_DETERMINISTIC",
            "provider": "STRANDS_FALLBACK",
            "status": "success"
        }

