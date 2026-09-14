# NOVA Automated Testing & Verification Suite

## 1. Test Suite Overview
The NOVA backend includes a comprehensive, automated test suite consisting of **32 test cases** across three test modules in `backend/tests/`. All 32 tests execute in under 4 seconds in an isolated, deterministic test fixture environment without requiring external network calls or paid API keys.

```bash
# Execute the full verification suite
python -m pytest backend/tests/ -v
```

**Verification Result:** `32 passed in ~3.4s` (100% pass rate).

---

## 2. Test File Inventory & Coverage

### A. Core Agent & Hero Scenarios (`test_agent_scenarios.py` - 17 tests)
Verifies the end-to-end Strands Agent tool executions, deterministic gating, and the three official hackathon user journeys:
1. `test_hero_1_milk_auto_buy`: Predictive Restock: Low milk triggers `AUTO` verdict, updates pantry, deducts budget, logs audit entry.
2. `test_hero_2_oil_restraint`: Intelligent Restraint: Healthy oil level (30 days remaining) triggers `DO_NOTHING`, preserves budget, logs restraint in audit ledger.
3. `test_hero_3_maggi_intent_reconciliation`: Intent Reconciliation: User intent "make Maggi tonight" decomposes recipe, verifies oil/spices in stock, buys only missing noodles.
4. `test_expensive_product_requires_ask`: Auto-buy threshold gate: Products exceeding ₹500 auto-limit return `ASK`.
5. `test_restricted_alcohol_blocked`: Safety policy gate: Blocked categories (e.g. Alcohol) return `BLOCKED` with zero commerce action.
6. `test_full_autopilot_vs_ask_everything`: Autonomy profile gate: Non-autopilot profile forces `ASK` even for valid low-stock items.
7. `test_budget_exhaustion_forces_ask`: Budget headroom gate: Proposed order exceeding remaining budget returns `ASK`.
8. `test_low_confidence_forces_ask`: Epistemic confidence gate: Low confidence prediction (< 0.70) forces `ASK`.
9. `test_price_signal_wait`: Price timing gate: Elevated price with ample household stock returns `WAIT`.
10. `test_audit_trail_captures_all_events`: Telemetry verification: All tool executions, verdicts, and reasons appear in the audit trail.
11. `test_category_policy_modification`: Governance tools: Policy changes via agent tool dynamically affect subsequent purchase evaluations.
12. `test_manage_reminders_tool`: Lifecycle verification: Reminder creation, snoozing, and dismissal through Strands tools.
13. `test_pantry_update_tools`: Pantry management: Updating item quantities and reporting items depleted.
14. `test_overview_tool`: Household overview: Aggregate stats for budget, reminders, and low-stock count.
15. `test_budget_status_tool`: Budget telemetry: Accurate reporting of spend, remaining balance, and pressure flags.
16. `test_price_watch_tool`: Market intelligence: Detection of price drops and timing recommendations.
17. `test_compare_offers_tool`: Cross-retailer comparison: Evaluation of prices across Swiggy, Blinkit, Zepto, and Amazon.

### B. Cooking & Activity Intent (`test_cooking_intent.py` - 8 tests)
Verifies natural language recipe deconstruction, household serving multipliers, and intelligent pantry deduction:
1. `test_poha_intent_with_peanuts`: Recipe parsing for Poha with healthy pantry staples.
2. `test_chai_intent_milk_already_stocked`: Chai preparation when milk is already stocked.
3. `test_biryani_scaling_for_large_group`: Scaled recipe intent (e.g. Biryani for 8 people) correctly calculates ingredient multiples.
4. `test_pasta_missing_cheese`: Pasta intent with partial pantry match (pasta in stock, cheese missing).
5. `test_unknown_intent_graceful_handling`: Unrecognized recipe/activity gracefully defaults without runtime crashes.
6. `test_empty_intent_handling`: Empty or whitespace-only queries handled safely.
7. `test_recipe_quantity_calculation`: Unit conversion and ingredient quantity calculations.
8. `test_recipe_availability_check`: Correct filtering of items already in healthy stock vs missing.

### C. System Hardening & Edge Cases (`test_hardening_and_fixes.py` - 7 tests)
Verifies input validation, boundary cases, and fault tolerance:
1. `test_negative_price_rejection`: Commerce gate rejects invalid or negative pricing.
2. `test_zero_quantity_handling`: Pantry service handles zero-quantity depletion safely.
3. `test_null_category_fallback`: Products with missing or null categories fallback to safe default handling.
4. `test_circuit_breaker_recovery`: Swiggy MCP adapter gracefully recovers from rate-limits and network timeouts.
5. `test_persistence_state_recovery`: State files recover gracefully from corrupt or missing JSON files.
6. `test_concurrent_cart_operations`: Multiple simultaneous cart additions maintain state consistency.
7. `test_policy_substring_matching`: Robust bidirectional substring matching for category rules (e.g., "Dairy" vs "Milk").

