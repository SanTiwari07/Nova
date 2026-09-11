# Multi-Agent Research Findings

During Phase 1, multiple specialized agents were invoked to research and design the architecture. Their findings are summarized below.

## Agent 1: Hackathon Strategy
- **Focus:** Autonomy, Memory, Proactivity.
- **Differentiator:** Proactive actions via EventBridge triggers, proving the agent isn't just a reactive chatbot.
- **Recommendation:** Implement a "Sunday Evening Reset" scenario to demonstrate reasoning, memory, and proactivity.

## Agent 2: Agent Architecture
- **Focus:** The boundary between LLM and deterministic layers.
- **Constraint:** The LLM must *never* have unrestricted ability to spend money.
- **Recommendation:** LLM handles intent and planning, then proposes a cart to a deterministic tool. The tool evaluates exact prices and policies before executing.

## Agent 3: Household Intelligence
- **Focus:** State, inventory, and consumption modeling.
- **Constraint:** Avoid over-engineering ML for the MVP.
- **Recommendation:** Use a Moving Average Daily Consumption Rate (DCR). Decay confidence over time. Compare `Estimated_Current_Quantity` with `Reorder_Threshold` to trigger actions.

## Agent 4: Autonomy / Safety / Policy
- **Focus:** Never silently bypass user rules.
- **Constraint:** Default to zero (safe failure).
- **Recommendation:** Define 5 states (`AUTO`, `ASK`, `WAIT`, `DO_NOTHING`, `BLOCKED`). Any budget breach, category restriction, or low confidence immediately forces an `ASK` or `BLOCKED` state.

## Agent 5: Product / UX Design
- **Focus:** Premium SaaS × Intelligent Assistant.
- **Constraint:** No sci-fi AI dashboards or terminal UIs.
- **Recommendation:** Use human language ("Running low", "Taken care of"). Use a calm color palette (off-white, deep charcoal) with an accent (Amazon orange) strictly for primary actions. Build trust through simple "Why did NOVA do this?" explanations.
