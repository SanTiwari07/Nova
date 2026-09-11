# NOVA Security and Authorization Model

## 1. Core Principle
**NOVA must never silently bypass user rules.**
The deterministic authorization layer is the final authority. The LLM can *propose* a cart or an action, but it can never execute a state-changing transaction without passing the deterministic checks.

## 2. Authorization Layer
- **Contextual Auth:** Every action requires a securely authenticated context mapping to a household ID.
- **No Direct API Keys for LLM:** The LLM does not hold Stripe, Swiggy, or Amazon API keys. It requests action via a tool, and the tool backend securely signs and executes the request.
- **Delegation Tiers:** Users configure strict auto-approve limits (e.g., `< ₹500`). Anything exceeding limits shifts to `ASK`.

## 3. Safe Failure (Default-to-Zero)
- If a rule evaluation fails, the system defaults to `ASK` or `BLOCKED`. It never defaults to `AUTO`.
- **Velocity Locks:** Hard limits on purchase frequency (e.g., max 3 orders/24h) prevent runaway agent loops.

## 4. Policy Engine Constraints
- **Budget Caps:** Daily, weekly, monthly transaction limits.
- **Category Restrictions:** Allow/Deny lists (e.g., alcohol blocked).
- **Conflict Resolution:** If rules conflict, the most restrictive rule wins, or the system defaults to `ASK`.

## 5. Auditability
- **Immutable Ledger:** Every state transition (Intent $\rightarrow$ Execution) is logged.
- The user can always query "Why did NOVA do this?" and see the exact rule or condition that triggered the state.
