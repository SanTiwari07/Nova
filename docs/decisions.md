# NOVA Architecture Decisions

## Decision 1: Strict Separation of LLM and Deterministic Logic
**Context:** We need NOVA to be autonomous but completely safe regarding budget and policy.
**Decision:** The LLM (via Bedrock + Strands SDK) handles NLU, intent, reasoning, and planning. Deterministic code handles math, policy enforcement, budget checks, and commerce execution.
**Reasoning:** LLMs hallucinate math and cannot be trusted with an open checkbook. A strict boundary prevents runaway spend and ensures safety.

## Decision 2: Feature-Based Backend Organization
**Context:** The backend could easily turn into a massive monolithic ball of mud.
**Decision:** Organize backend by feature domain (`household/`, `inventory/`, `intent/`, `decision/`, `commerce/`, `memory/`, `policy/`, `budget/`, `audit/`). Each feature owns its models, schemas, services, and tests.
**Reasoning:** Promotes separation of concerns, scalability, and easier maintenance. 

## Decision 3: Event-Driven Proactivity
**Context:** NOVA must act proactively, not just as a reactive chatbot.
**Decision:** Use Amazon EventBridge to trigger Lambda workflows that wake up the NOVA Agent.
**Reasoning:** Demonstrates true autonomy without user prompting.

## Decision 4: Moving Average Daily Consumption Rate (DCR) over ML
**Context:** Inventory forecasting requires predicting when items run out.
**Decision:** Use a deterministic DCR approach rather than a complex ML model for MVP.
**Reasoning:** Simple, predictable, easy to explain to users, and perfectly sufficient for household goods. Avoids over-engineering.

## Decision 5: The "Ask" Fallback State
**Context:** What happens when rules conflict, confidence is low, or inventory is uncertain?
**Decision:** Default to an `ASK` state where NOVA requires explicit user approval.
**Reasoning:** "NOVA must never silently bypass user rules." It prioritizes trust and safety over absolute automation.

## Decision 6: Abstracted Commerce Interface
**Context:** Integrating directly with one provider (e.g., Swiggy, Amazon) couples the system too tightly.
**Decision:** Create a `CommerceInterface` with mock adapters for development and real adapters for production.
**Reasoning:** Allows rapid MVP development and testing without real financial transactions, and makes future provider integration seamless.
