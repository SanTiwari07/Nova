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

## 17. Memory & State Architecture
NOVA manages state across two complementary tiers:
- **Local Runtime State (Active):**
  - **Household Memory:** Persistent recurring item habits, typical reorder intervals, preferred brands, and historical purchase prices loaded via `MockAmazonHistoryProvider` (`backend/amazon/history_service.py`).
  - **Deterministic State Ledgers:** Inventory quantities, consumption velocities, and budget spend are stored in persistent local JSON state files (`backend/data/*_state.json`) with deterministic in-memory indexing.
  - **Session State:** Autonomy profiles (`FULL_AUTOPILOT`, `ASK_EVERYTHING`, `RESTRICTIVE`) and active UI sessions tracked via `UserSessionService`.
- **Cloud Deployment Mapping (AgentCore Blueprint):**
  - Designed to map to **AWS Bedrock AgentCore Memory** for semantic recall and **Amazon DynamoDB** for scalable multi-tenant household state.

## 18. Audit Architecture
Every significant decision is logged to provide full explainability.
Fields logged: timestamp, household_id, intent, requested_action, inventory_context, confidence, budget_context, policy_result, authorization_result, decision, commerce_result, and natural language reason.

## 19. Proactive Execution Workflow
Proactivity operates at two levels:
- **Local Environment:** Automated background sweeps and monthly planning cycles are triggered through `/api/autopilot/monthly-plan`, `/api/autopilot/run-cycle`, or interactive schedule sweeps.
- **Production Cloud Architecture:** Designed to trigger via **Amazon EventBridge** cron rules invoking an AWS Lambda orchestration handler that wakes the NOVA Strands Agent.

## 20. Technology Stack & AWS Mapping
- **Agent Framework:** AWS Strands Agents SDK (`from strands import Agent`, `BeforeToolCallEvent`, `AfterToolCallEvent`).
- **Foundation Models:** Amazon Bedrock (Claude 3.5 Sonnet v2) and Google Gemini (gemini-2.5-flash), with offline deterministic tool dispatch fallback.
- **API Gateway:** FastAPI with asynchronous streaming SSE/NDJSON endpoints.
- **Frontend Command Center:** Next.js 14 App Router, TypeScript, Tailwind CSS (24 static prerendered routes).
- **Commerce Protocol:** Model Context Protocol (MCP) Streamable HTTP / JSON-RPC 2.0 with OAuth 2.1 PKCE.
- **Cloud Reference Blueprint:** AWS Bedrock AgentCore Action Groups, Bedrock AgentCore Memory, Amazon EventBridge, and DynamoDB.

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

![NOVA Autonomous Household Decision Architecture](nova_system_architecture.png)

*16:9 Presentation-Ready Architecture Diagram — Built for the AWS Agents for Humans Hackathon (Everyday Agents Track).*  
*Formats available:* [SVG Vector](nova_system_architecture.svg) | [Interactive HTML Viewer](nova_system_architecture.html) | [High-Res PNG](nova_system_architecture.png)

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
