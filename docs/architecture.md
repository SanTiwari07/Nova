# NOVA Architecture

## 6. Agent Definition
NOVA is built around a primary intelligent agent using the Strands Agents SDK and Amazon Bedrock. 
The LLM handles: understanding natural language, recognizing intent, reasoning about goals, generating plans, interpreting context, and explaining decisions.
Deterministic code handles: exact math, budget calculation, consumption tracking, policy validation, authorization, commerce execution, and state updates.

## 8. Final Production Agent Architecture
The architecture avoids unnecessary multi-agent orchestration. It uses ONE PRIMARY NOVA AGENT augmented by domain services, deterministic tools, memory, policy, and commerce modules.

### Logical Boundary
**LLM (Probabilistic):**
- Natural Language Understanding
- Intent Recognition
- Reasoning & Planning
- Explanation

**Code (Deterministic):**
- Calculations & Math
- Policy Validation
- Commerce Execution
- State Management

## 16. Commerce Architecture
Commerce logic is abstracted behind `CommerceInterface`:
```python
search_products()
get_product()
check_availability()
create_cart()
get_cart()
checkout()
track_order()
```
The agent interacts with tools that call this interface. We use `mock_adapter.py` for development and demos, clearly separated from `swiggy_adapter.py` or other real integrations.

## 17. Memory Architecture
NOVA uses AgentCore Memory to store persistent useful context:
- Preferred products and brands
- Household routines and preferences
- Implicit approvals and corrections
Memory is queryable by the LLM for context enrichment. It does not store real-time inventory levels, which are kept in deterministic DynamoDB tables.

## 18. Audit Architecture
Every significant decision is logged to provide full explainability.
Fields logged: timestamp, household_id, intent, requested_action, inventory_context, confidence, budget_context, policy_result, authorization_result, decision, commerce_result, and natural language reason.

## 19. Event Workflow
Event-driven autonomy is handled via Amazon EventBridge -> Lambda/Workflow -> NOVA Agent.
1. Event triggers (e.g., daily check).
2. NOVA retrieves household state.
3. Evaluates needs.
4. Deterministic decision engine evaluates rules.
5. Emits outcome: AUTO / ASK / WAIT / DO_NOTHING / BLOCKED.

## 20. AWS Architecture
- **Amazon Bedrock**: LLM hosting.
- **Strands Agents SDK & AgentCore**: Runtime, memory, and gateway.
- **DynamoDB**: Household state, inventory, rules, budget, audit logs.
- **AWS Lambda & EventBridge**: Background workflows and scheduling.

## 21. Frontend Architecture
Next.js (React) application.
- `frontend/app/`: Next.js app router structure (page.tsx, pantry, plans, orders, budget, rules).
- `frontend/components/`: Reusable UI components grouped by feature (household, pantry, plans, orders, budget, rules, activity, explanations).
- `frontend/lib/api/`: Domain-specific API clients.

## 22. Backend Architecture
Python FastAPI application organized strictly by feature domain.
- `backend/agent/`: Prompts, tools, config.
- `backend/household/`, `backend/inventory/`, `backend/intent/`, `backend/decision/`, `backend/commerce/`, `backend/memory/`, `backend/budget/`, `backend/policy/`, `backend/audit/`: Feature folders owning their own models, schemas, services, and routes.
- `backend/workflows/`: Background tasks.
- `backend/api/`: Main FastAPI app and dependencies.

## Architecture Diagram
```text
                         USER
                          │
                          ▼
                  ┌───────────────┐
                  │     NOVA      │
                  │   Frontend    │
                  │ Premium SaaS  │
                  └───────┬───────┘
                          │
                          ▼
                ┌──────────────────┐
                │   NOVA AGENT     │
                │ Strands +        │
                │ Bedrock          │
                └────────┬─────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
     Household       Inventory        Intent
       State        + Consumption    + Needs
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 ┌──────────────┐
                 │   DECISION   │
                 │    LAYER     │
                 └──────┬───────┘
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
        Budget        Policy    Authorization
           │            │            │
           └────────────┼────────────┘
                        ▼
                    Commerce
                        │
                        ▼
                  State Update
                   │         │
                   ▼         ▼
                Memory     Audit

EventBridge
     ↓
Lambda / Workflow
     ↓
NOVA Agent
```
