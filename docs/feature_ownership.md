# NOVA Feature Ownership Rules

**Mandatory Rule:** Each feature owns its domain. There is no generic `models/` or `services/` folder where all features are mixed.

## Household
**Owns:** Household model, members, preferences, household context, household state.

## Inventory
**Owns:** Pantry, quantity, stock state, consumption, forecast, confidence.

## Intent
**Owns:** Natural-language intent, intent parsing, requirements, goals.

## Decision
**Owns:** Decisions, budget validation, policy validation, authorization, `AUTO`/`ASK`/`WAIT`/`DO_NOTHING`/`BLOCKED` states.

## Commerce
**Owns:** Products, search, availability, cart, checkout, tracking, provider adapters.

## Memory
**Owns:** Persistent useful context, preferences, history, learned household information.

## Budget
**Owns:** Budget state, spending, limits, transaction accounting.

## Policy
**Owns:** User rules, restrictions, autonomy constraints.

## Audit
**Owns:** Decision history, action history, explainability records.
