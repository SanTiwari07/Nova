# NOVA
## The intelligence layer for everyday life.

### 1. Product Definition
NOVA is an intelligence layer that understands everyday household context and takes care of routine decisions within the user's rules. The initial MVP focuses on the "Household Autopilot" capability.

### 2. NOVA Brand Definition
**Name**: NOVA
**Tagline**: The intelligence layer for everyday life.
NOVA feels like a premium consumer product. It quietly understands the user's life and acts gracefully. It avoids aggressive "AI" branding—no robot imagery, no glowing effects, no "AGENT ONLINE" labels.

### 3. Problem Statement
Managing a household requires constant context retrieval, planning, and micro-decisions (What do we have? What do we need? Are we on budget?). Traditional apps require manual data entry, while basic AI agents lack deterministic constraints and deep context.

### 4. Differentiation
- **Autonomy ≠ Automation**: NOVA knows when to ACT, ASK, WAIT, DO NOTHING, or BLOCK.
- **Deterministic Decision Layer**: The LLM reasons, but deterministic code controls spending and rules.
- **Premium SaaS UX**: Calm, invisible intelligence over a dense enterprise dashboard.
- **Context-Aware**: Uses inventory, consumption, confidence, budget, policy, and intent before acting.

### 5. User Journeys
- **Autonomous Action**: NOVA notices an item is low, checks budget/policy, and automatically purchases it.
- **No Action Needed**: NOVA evaluates an item, determines stock is sufficient, and records "No action needed."
- **Intent to Action**: User says "I want to make Maggi tonight." NOVA identifies requirements, checks pantry, and proposes actions for missing items.

### 26. MVP Definition
- NOVA primary agent (Strands Agents SDK + Bedrock).
- Household state, inventory, consumption, confidence, intent, budget, policy, authorization.
- Deterministic decision engine (AUTO, ASK, WAIT, DO_NOTHING, BLOCKED).
- Commerce abstraction with mock commerce.
- Audit trails and background workflows (EventBridge).
- Premium frontend.
- Three E2E demo scenarios.

### 27. Out-of-Scope Definition
- Multiple retailers
- Advanced computer vision / receipt OCR / barcode scanning
- Smart refrigerator / smart home integrations
- Advanced ML forecasting
- Complicated multi-agent production architecture
- Unnecessary identity features and AWS services

### 33. Phase 2 Implementation Roadmap
1. Repository foundation
2. Backend/API foundation
3. Household state
4. Inventory
5. Consumption
6. Confidence
7. Intent
8. Requirements
9. Budget
10. Policy
11. Authorization
12. Decision engine
13. Commerce interface
14. Mock commerce
15. NOVA agent
16. Agent tools
17. Memory
18. Audit
19. EventBridge workflow
20. Frontend foundation
21. NOVA home experience
22. Pantry
23. Plans
24. Orders
25. Budget
26. Rules
27. Explanation experience
28. Backend/frontend integration
29. Tests
30. End-to-end demo
31. AWS/AgentCore integration
32. Deployment
33. Demo hardening
